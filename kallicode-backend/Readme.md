# Nombre del proyecto: Alloxentric Real Time Agent 

## Descripcion y objetivo del proyecto
Engine de agente conversacional de voz en tiempo real que permite escuchar, comprender y responder a los usuarios mediante voz natural, buscando una interaccino fluida y de baja latencia. Integra reconocimiento de voz, un LLM para generar respuestas y tecnologias de sistesis de voz como elevenlab y tacotron.

Dirigido a: Empresas y organizaciones que requieran automatizar comunicaciones por voz, como atencion al cliente, cobranza, agendamiento, encuestas y soporte de primer nivel

Problema que resuelve: Automatiza conversaciones telefonicas y de atencion al cliente, reduciendo costos operacionales y tiempos de atencion, ademas de permitir interacciones de voz mas naturales y escalables

## Tecnologias utilizadas
* Lenguajes: Python
* Backend: FastAPI
* Streaming: WebSocket / WebRTC
* ASR/STT: Whisper u otro servicio cloud
* LLM: API de modelo de lenguaje
* TTS: ElevenLabs y Tacotron 2
* Vocoder: HiFi-GAN o WaveGlow
* Machine Learning: PyTorch
* Infraestructura: GPU para síntesis de voz auto-hospedada
* Base de datos: No especificada en el alcance actual
* Cloud: Servicios cloud para ASR y APIs de IA, según implementación final

