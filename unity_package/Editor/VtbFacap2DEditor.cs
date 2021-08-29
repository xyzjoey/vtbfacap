using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;

namespace VtbFacap
{
    [CustomEditor(typeof(VtbFacap2D))]
    public class VtbFacap2DEditor : Editor
    {
        public override void OnInspectorGUI()
        {
            base.OnInspectorGUI();

            var script = (VtbFacap2D)this.target;

            var previousGUIState = GUI.enabled;
            if (Application.isPlaying) GUI.enabled = false;

            if(GUILayout.Button("Load Config File", GUILayout.Height(20)))
            {
                Undo.RecordObject(script, "Change config");
                script.config.LoadConfig(script.configFile.ToString());
                EditorUtility.SetDirty(script);  // FIXME without this line cannot preserve change in play mode
                PrefabUtility.RecordPrefabInstancePropertyModifications(script);
            }
            
            if(GUILayout.Button("Overwrite Config File", GUILayout.Height(20)))
            {
                if (script.configFile == null)
                {
                    throw new Exception("[VtbFacap] configFile has not been assigned.");
                }

                script.config.SaveConfigFile(AssetDatabase.GetAssetPath(script.configFile));
            }

            if(GUILayout.Button("Create Config File", GUILayout.Height(20)))
            {
                // find path to create file
                string targetDir = "Assets";
                string prefabPath = AssetDatabase.GetAssetPath(PrefabUtility.GetCorrespondingObjectFromOriginalSource(script.gameObject));

                if (!string.IsNullOrEmpty(prefabPath) && !prefabPath.StartsWith("Packages"))
                {
                    targetDir = Path.GetDirectoryName(prefabPath);
                }

                string name = script.gameObject.name;
                string ext = ".vtbfacap.json";
                string configFilePath = Path.Combine(targetDir, name + ext);

                int i = 1;
                while (File.Exists(configFilePath))
                {
                    configFilePath = Path.Combine(targetDir, name + i + ext);
                    ++i;
                }

                // create & load
                AssetDatabase.CopyAsset("Packages/xyzjoey.vtbfacap/Samples/default.vtbfacap.json", configFilePath);
                script.configFile = AssetDatabase.LoadAssetAtPath<TextAsset>(configFilePath);
                script.config.LoadConfig(script.configFile.ToString());
                Debug.Log("[VtbFacap] Created config at " + configFilePath);
            }

            if (Application.isPlaying) GUI.enabled = previousGUIState;
        }
    }
}
