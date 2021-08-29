# vtuber-face-mocap
Facial motion capture with webcam for VTuber in unity/unreal.

<img src="images\live2d_mouth_eyeblink.gif" height="300">

## Run
python
```
cd python_vtbfacap
pip install -r requirements.txt
HIDE_FACE=false python -m vtbfacap
```

unity --> see unity_package/README.md

## TODO
- [x] obtain landmarks (mediapipe python)
- [ ] convert landmarks to blendshape data (2D) [head rotation done]
- [ ] convert landmarks to blendshape data (3D)
- [ ] calibration
- [ ] unity package (2D)
- [ ] unity package (3D)
- [ ] (optional) unreal package (2D)
- [ ] unreal package (3D)
- [ ] save data sequence for replay

## Reference
https://github.com/google/mediapipe

https://github.com/Kazuhito00/iris-detection-using-py-mediapipe
