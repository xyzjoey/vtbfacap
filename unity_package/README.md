## Run (Live2D)
1. Add scoped registry (Project Settings > Package Manager) 
```
// manifest.json
  "scopedRegistries": [
    {
      "name": "openupm",
      "url": "https://package.openupm.com",
      "scopes": [
        "com.azixmcaze",
        "jillejr.newtonsoft"
      ]
    }
  ]
```
2. Install cubism package and this package (Package Manager Window > Add package from git URL > add https://github.com/grashaar/CubismUnityComponents-CubismLoader.git?path=/Assets/Live2D#upm and https://github.com/xyzjoey/vtbfacap.git?path=/unity_package)
3. Remove cubism sample models and import your model (see https://docs.live2d.com/cubism-sdk-tutorials/getting-started/?locale=en_us)
4. Set camera projection to orthographic
5. Add VtbFacap script to model (Add Component > VtbFacap2D) and press "Create Config File"
6. Run python vtbfacap and play unity scene
