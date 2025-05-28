class VoiceBridge {
    constructor() {
        this.ws = null;
        this.audioContext = null;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.isConnected = false;
        
        this.initializeElements();
        this.connectWebSocket();
        this.setupEventListeners();
    }
    
    initializeElements() {
        this.statusEl = document.getElementById('status');
        this.conversationEl = document.getElementById('conversation');
        this.talkButton = document.getElementById('talkButton');
        this.clearButton = document.getElementById('clearButton');
        this.summaryButton = document.getElementById('summaryButton');
        this.visualizerEl = document.getElementById('visualizer');
        this.audioBars = this.visualizerEl.querySelectorAll('.audio-bar');
    }
    
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            this.isConnected = true;
            this.updateStatus('Connected', true);
            this.talkButton.disabled = false;
            this.addMessage('Connected to voice bridge', 'system');
        };
        
        this.ws.onmessage = async (event) => {
            const message = JSON.parse(event.data);
            await this.handleMessage(message);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.addMessage('Connection error', 'system');
        };
        
        this.ws.onclose = () => {
            this.isConnected = false;
            this.updateStatus('Disconnected', false);
            this.talkButton.disabled = true;
            this.addMessage('Connection closed. Refreshing page...', 'system');
            setTimeout(() => location.reload(), 2000);
        };
    }
    
    setupEventListeners() {
        // Talk button - both mouse and touch events
        this.talkButton.addEventListener('mousedown', () => this.startRecording());
        this.talkButton.addEventListener('mouseup', () => this.stopRecording());
        this.talkButton.addEventListener('mouseleave', () => this.stopRecording());
        
        this.talkButton.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.startRecording();
        });
        this.talkButton.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.stopRecording();
        });
        
        // Control buttons
        this.clearButton.addEventListener('click', () => this.clearContext());
        this.summaryButton.addEventListener('click', () => this.getSummary());
    }
    
    async startRecording() {
        if (!this.isConnected || this.isRecording) return;
        
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    channelCount: 1,
                    sampleRate: 16000,
                    echoCancellation: true,
                    noiseSuppression: true
                } 
            });
            
            this.audioContext = new AudioContext({ sampleRate: 16000 });
            const source = this.audioContext.createMediaStreamSource(stream);
            const processor = this.audioContext.createScriptProcessor(4096, 1, 1);
            
            processor.onaudioprocess = (e) => {
                if (!this.isRecording) return;
                
                const inputData = e.inputBuffer.getChannelData(0);
                const pcmData = this.float32ToPCM16(inputData);
                
                if (this.ws.readyState === WebSocket.OPEN) {
                    this.ws.send(JSON.stringify({
                        type: 'audio',
                        data: this.arrayBufferToBase64(pcmData.buffer)
                    }));
                }
                
                this.updateVisualizer(inputData);
            };
            
            source.connect(processor);
            processor.connect(this.audioContext.destination);
            
            this.isRecording = true;
            this.talkButton.classList.add('recording');
            this.visualizerEl.style.display = 'flex';
            
        } catch (error) {
            console.error('Error accessing microphone:', error);
            this.addMessage('Error accessing microphone. Please check permissions.', 'system');
        }
    }
    
    stopRecording() {
        if (!this.isRecording) return;
        
        this.isRecording = false;
        this.talkButton.classList.remove('recording');
        this.visualizerEl.style.display = 'none';
        
        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }
    }
    
    float32ToPCM16(float32Array) {
        const pcm16 = new Int16Array(float32Array.length);
        for (let i = 0; i < float32Array.length; i++) {
            const s = Math.max(-1, Math.min(1, float32Array[i]));
            pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }
        return pcm16;
    }
    
    arrayBufferToBase64(buffer) {
        const bytes = new Uint8Array(buffer);
        let binary = '';
        for (let i = 0; i < bytes.byteLength; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return btoa(binary);
    }
    
    updateVisualizer(audioData) {
        const average = audioData.reduce((a, b) => Math.abs(a) + Math.abs(b)) / audioData.length;
        const normalized = Math.min(1, average * 10);
        
        this.audioBars.forEach((bar, index) => {
            const height = 5 + (normalized * 35) + (Math.random() * 10);
            bar.style.height = `${height}px`;
        });
    }
    
    async handleMessage(message) {
        switch (message.type) {
            case 'transcription':
                this.addMessage(message.text, 'user');
                break;
                
            case 'response':
                this.addMessage(message.text, 'assistant');
                break;
                
            case 'audio':
                await this.playAudio(message.data);
                break;
                
            case 'status':
                this.addMessage(message.message, 'system');
                break;
                
            case 'summary':
                this.showSummary(message.data);
                break;
                
            case 'error':
                this.addMessage(`Error: ${message.message}`, 'system');
                break;
        }
    }
    
    async playAudio(base64Audio) {
        try {
            const audioData = atob(base64Audio);
            const arrayBuffer = new ArrayBuffer(audioData.length);
            const view = new Uint8Array(arrayBuffer);
            
            for (let i = 0; i < audioData.length; i++) {
                view[i] = audioData.charCodeAt(i);
            }
            
            const audioBlob = new Blob([arrayBuffer], { type: 'audio/mpeg' });
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);
            
            await audio.play();
            
            audio.onended = () => {
                URL.revokeObjectURL(audioUrl);
            };
            
        } catch (error) {
            console.error('Error playing audio:', error);
        }
    }
    
    addMessage(text, type) {
        const messageEl = document.createElement('div');
        messageEl.className = `message ${type}`;
        messageEl.textContent = text;
        
        this.conversationEl.appendChild(messageEl);
        this.conversationEl.scrollTop = this.conversationEl.scrollHeight;
    }
    
    updateStatus(text, connected) {
        this.statusEl.textContent = text;
        this.statusEl.classList.toggle('connected', connected);
    }
    
    clearContext() {
        if (this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'control',
                action: 'clear_context'
            }));
        }
    }
    
    getSummary() {
        if (this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'control',
                action: 'get_summary'
            }));
        }
    }
    
    showSummary(data) {
        const duration = Math.floor(data.session_duration / 60);
        const summaryText = `Session Summary: ${data.message_count} messages over ${duration} minutes`;
        this.addMessage(summaryText, 'system');
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    new VoiceBridge();
});