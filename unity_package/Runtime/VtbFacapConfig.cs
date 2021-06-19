// using GD.MinMaxSlider;
using Newtonsoft.Json;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace VtbFacap{
    [System.Serializable]
    public class OutputParam
    {
        // [MinMaxSlider(0f, 1f)]  // ident --> can't see values
        // public Vector2 minMax = new Vector2(0f, 1f);
        [Range(0f, 1f)]
        public float min;
        [Range(0f, 1f)]
        public float max;
        [Range(-1f, 1f)]
        public float mean = 0;
        [Range(0f, 1f)]
        public float smooth;
    }

    [System.Serializable]
    public class ParamMapItem : SerializableDictionary<string, OutputParam> {}

    [System.Serializable]
    public class ParamMap : SerializableDictionary<string, ParamMapItem> {}

    [CreateAssetMenu(fileName="NewVtbFacapConfig", menuName="VtbFacapConfig")]
    public class VtbFacapConfig : ScriptableObject
    {
        public TextAsset configFile;
        public ParamMap paramMap = new ParamMap();
        
        public void LoadConfigFile()
        {
            var result = JsonConvert.DeserializeObject<dynamic>(this.configFile.ToString());
            this.paramMap.Clear();
            
            foreach (var blendshapeConfig in result["paramMap"])
            {
                this.paramMap[blendshapeConfig.Name] = new ParamMapItem();
                foreach (var outputParamConfig in blendshapeConfig.Value)
                {
                    OutputParam outputParam = new OutputParam();
                    outputParam.min = outputParamConfig.Value["min"];
                    outputParam.max = outputParamConfig.Value["max"];
                    outputParam.mean = outputParamConfig.Value["mean"];
                    outputParam.smooth = outputParamConfig.Value["smooth"];
                    this.paramMap[blendshapeConfig.Name][outputParamConfig.Name] = outputParam;
                }
            }
        }

        public void SaveConfigFile(string path)
        {
            File.WriteAllText(
                path,
                JsonConvert.SerializeObject(new Dictionary<string, dynamic> {{"paramMap", this.paramMap}}, Formatting.Indented)
            );
        }

        public IEnumerable IterParamMapWithIndex()
        {
            int i = 0;
            foreach (var paramMapPair in this.paramMap)
            {
                yield return (Index: i++, Key: paramMapPair.Key, Value: paramMapPair.Value);
            }
        }
    }
}
