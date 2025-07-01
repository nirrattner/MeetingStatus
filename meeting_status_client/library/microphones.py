import AVFoundation
import CoreAudio
import struct

AUDIO_OBJECT_PROPERTIES = CoreAudio.AudioObjectPropertyAddress(
  CoreAudio.kAudioDevicePropertyDeviceIsRunningSomewhere,
  CoreAudio.kAudioObjectPropertyScopeGlobal,
  CoreAudio.kAudioObjectPropertyElementMaster
)

def is_any_microphone_active() -> bool:
  for microphone in AVFoundation.AVCaptureDevice.devicesWithMediaType_(AVFoundation.AVMediaTypeAudio):
    microphone_data = CoreAudio.AudioObjectGetPropertyData(
        microphone.connectionID(),
        AUDIO_OBJECT_PROPERTIES,
        0,
        [],
        4,
        None)
    is_microphone_active = bool(struct.unpack('I', microphone_data[2])[0])
    if is_microphone_active:
      return True
  return False



