using UnityEngine;
using UnityEditor;

namespace VtbFacap
{
    public class Utils
    {
        public static void SmoothCurve(AnimationCurve curve)
        {
            if (curve.length == 0) return;

            AnimationUtility.SetKeyRightTangentMode(curve, 0, AnimationUtility.TangentMode.Linear);
            AnimationUtility.SetKeyLeftTangentMode(curve, curve.length - 1, AnimationUtility.TangentMode.Linear);

            for (int i = 1; i < curve.length - 1; ++i)
            {
                AnimationUtility.SetKeyLeftTangentMode(curve, i, AnimationUtility.TangentMode.ClampedAuto);
                AnimationUtility.SetKeyRightTangentMode(curve, i, AnimationUtility.TangentMode.ClampedAuto);
            }
        }
    }
}
