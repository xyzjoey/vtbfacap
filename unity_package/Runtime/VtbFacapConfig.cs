using Newtonsoft.Json;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;

namespace VtbFacap
{
    using FacapDataFieldName = System.String;
    using ParamName = System.String;

    [System.Serializable]
    public class ParamValue
    {
        [Readonly, JsonIgnore]
        public float raw = 0f;  // for showing input value
        [Readonly, JsonIgnore]
        public float rawAfterCalibrate = 0f;  // for showing input value
        [ClampedCurveAttribute(0f, 0f, 1f, 1f, "map value from x axis to y axis")]
        public AnimationCurve control = AnimationCurve.Linear(0f, 0f, 1f, 1f);
        [Range(0f, 1f)]
        public float smooth = 0.15f;
        [Range(-1f, 1f)]
        public float calibrate = 0f;
    }

    [System.Serializable]
    public class ParamMap : SerializableDictionary<ParamName, ParamValue> {}

    [System.Serializable]
    public class FaceMap : SerializableDictionary<FacapDataFieldName, ParamMap>
    {
        public int IndexOf(FacapDataFieldName key)
        {
            return this.Keys.ToList().IndexOf(key);
        }
    }

    [System.Serializable]
    public class VtbFacapConfigData
    {
        [ClampedCurveAttribute(0f, 0f, 1f, 1f, "map left right eye difference to sync value")]
        public AnimationCurve eyeSync = AnimationCurve.Linear(0.299f, 1f, 0.3f, 0f);
        public FaceMap faceMap = new FaceMap();

        public string Serialize()
        {
            return JsonConvert.SerializeObject((VtbFacapConfigData)this, new VtbFacapConfigSerializationSettings());
        }

        static public VtbFacapConfigData Deserialize(string json)
        {
            return JsonConvert.DeserializeObject<VtbFacapConfigData>(json, new VtbFacapConfigSerializationSettings());
        }
    }

    [System.Serializable]
    public class VtbFacapConfig : VtbFacapConfigData
    {
        public void LoadConfig(string data)
        {
            VtbFacapConfigData result = VtbFacapConfigData.Deserialize(data);
            this.eyeSync = result.eyeSync;
            this.faceMap = result.faceMap;
        }

        public void SaveConfigFile(string path)
        {
            File.WriteAllText(path, this.Serialize());
            Debug.Log("[VtbFacap] Write config to " + path);
        }
    }
}
