using UnityEngine;

namespace VtbFacap
{
    public class ClampedCurveAttribute : PropertyAttribute
    {
        public Rect ranges;
        public string tooltip;

        public ClampedCurveAttribute(float xMin, float yMin, float xMax, float yMax, string tooltip)
        {
            this.ranges = new Rect(xMin, yMin, xMax, yMax);
            this.tooltip = tooltip;
        }
    }  
}
