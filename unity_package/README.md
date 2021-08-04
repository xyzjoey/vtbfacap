## Getting Started
1. Add scoped registry (Project Settings > Package Manager) 
```
// manifest.json
  "scopedRegistries": [
    {
      "name": "openupm",
      "url": "https://package.openupm.com",
      "scopes": [
        "com.live2d",
        "com.azixmcaze",
        "jillejr.newtonsoft"
      ]
    }
  ]
```
2. Install this package (Package Manager Window > Add package from git)
3. Remove cubism sample models and import your live2d model (see https://docs.live2d.com/cubism-sdk-tutorials/getting-started/?locale=en_us)
4. Set camera projection to orthographic
5. Add script to model (Add Component > VtbFacap) --> create VtbFacapConfig (Create > VtbFacapConfig) and drag to VtbFacap script --> drag Packages/VtbFacap/Samples/default.vtbfacap to VtbFacapConfig.ConfigFile and press "Load Config File"  // to be simplified
6. Play scene
