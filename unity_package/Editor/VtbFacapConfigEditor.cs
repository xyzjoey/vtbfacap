using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace VtbFacap{
    [CustomEditor(typeof(VtbFacapConfig))]
    public class VtbFacapConfigEditor : Editor
    {
        public override void OnInspectorGUI()
        {
            base.OnInspectorGUI();
            var script = (VtbFacapConfig)target;

            if(GUILayout.Button("Load Config File", GUILayout.Height(40)))
            {
                script.LoadConfigFile();
            }
            
            if(GUILayout.Button("Overwrite Config File", GUILayout.Height(40)))
            {
                script.SaveConfigFile(AssetDatabase.GetAssetPath(script.configFile));
            }
        }
    }
}
