using System.Linq;
using UnityEngine;
using UnityEditor;

namespace VtbFacap
{
    [CustomPropertyDrawer(typeof(ClampedCurveAttribute))]
    public class ClampedCurveDrawer : PropertyDrawer
    {
        public override void OnGUI(Rect position, SerializedProperty property, GUIContent label)
        {
            var attr = (ClampedCurveAttribute)attribute;
            label.tooltip = $"{attr.tooltip}\nrange: ({attr.ranges.xMin}, {attr.ranges.yMin}) to ({attr.ranges.xMax}, {attr.ranges.yMax})";

            // layout
            float height = position.height / 3;
            Rect fieldRect = EditorGUI.PrefixLabel(position, label);
            Rect rect1 = new Rect(fieldRect.x, fieldRect.y, fieldRect.width, height);
            Rect rect2 = new Rect(fieldRect.x, rect1.y + height, fieldRect.width, height);
            Rect rect3 = new Rect(position.x, rect2.y + height, position.width, height);
            GUIContent[] subLabels1 = {new GUIContent("first x"), new GUIContent("y")};
            GUIContent[] subLabels2 = {new GUIContent("last x"), new GUIContent("y")};
            GUIContent dummyLabel = new GUIContent(" ");

            // values
            AnimationCurve curve = property.animationCurveValue;
            Keyframe[] keys = curve.keys;
            int last = keys.Length - 1;
            float[] firstPoint = {keys[0].time, keys[0].value};
            float[] lastPoint = {keys[last].time, keys[last].value};

            EditorGUI.BeginChangeCheck();
            EditorGUI.MultiFloatField(rect1, subLabels1, firstPoint);
            EditorGUI.MultiFloatField(rect2, subLabels2, lastPoint);
            
            keys[0].time = Mathf.Clamp(firstPoint[0], attr.ranges.xMin, attr.ranges.xMax - 0.001f);
            keys[0].value = Mathf.Clamp(firstPoint[1], attr.ranges.yMin, attr.ranges.yMax);
            keys[last].time = Mathf.Clamp(lastPoint[0], keys[0].time + 0.001f, attr.ranges.xMax);
            keys[last].value = Mathf.Clamp(lastPoint[1], attr.ranges.yMin, attr.ranges.yMax);
            curve.keys = keys;

            curve = EditorGUI.CurveField(rect3, dummyLabel, curve, Color.white, attr.ranges);

            if (EditorGUI.EndChangeCheck() && curve.length >= 2)
            {
                Utils.SmoothCurve(curve);
                property.animationCurveValue = curve;
            }
        }

        public override float GetPropertyHeight(SerializedProperty property, GUIContent label)
        {
            return 3 * base.GetPropertyHeight(property, label);
        }
    }
}
