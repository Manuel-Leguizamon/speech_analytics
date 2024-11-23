from google.cloud import speech_v1p1beta1 as speech

def transcribe_diarization_gcs_beta(gcs_uri: str) -> bool:
    """Transcribe a remote audio file (stored in Google Cloud Storage) using speaker diarization.

    Args:
        gcs_uri: The Google Cloud Storage path to an audio file.

    Returns:
        True if the operation successfully completed, False otherwise.
    """

    client = speech.SpeechClient()

    speaker_diarization_config = speech.SpeakerDiarizationConfig(
        enable_speaker_diarization=True,
        min_speaker_count=2,
        max_speaker_count=2,
    )

    # Cambiar a MP3 para que coincida con el tipo de archivo
    recognition_config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="es-CO",
        diarization_config=speaker_diarization_config,
    )

    # Set the remote path for the audio file
    audio = speech.RecognitionAudio(
        uri=gcs_uri,
    )

    # Use non-blocking call for getting file transcription
    response = client.long_running_recognize(
        config=recognition_config, audio=audio
    ).result(timeout=300)

    # La transcripción y las etiquetas de hablantes
    if response.results:
        result = response.results[-1]
        words_info = result.alternatives[0].words

        # Guardar la salida en un archivo
        with open("salida.txt", "w", encoding="utf-8") as file:
            for word_info in words_info:
                file.write(f"{word_info.speaker_tag}:{word_info.word}\n")
        print("Se guardaron los resultados de la transcripcion en 'texto.txt'.")
        return True
    else:
        print("No se generaron resultados de transcripción. Verifica la calidad y el formato del audio.")
    return False
# URI del archivo en Google Cloud Storage
gcs_uri = "gs://bucketparacompiladores/mono_audio.wav"
transcribe_diarization_gcs_beta(gcs_uri)
