using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Newtonsoft.Json.Serialization;
using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace VtbFacap
{
    public class VtbFacapConfigControlConverter : JsonConverter<AnimationCurve>
    {
        public override void WriteJson(JsonWriter writer, AnimationCurve control, JsonSerializer serializer)
        {
            writer.WriteStartArray();

            foreach (var key in control.keys)
            {
                writer.WriteStartArray();
                writer.Formatting = Formatting.None;
                writer.WriteValue(key.time);
                writer.WriteValue(key.value);
                writer.WriteEndArray();
                writer.Formatting = Formatting.Indented;
            }

            writer.WriteEndArray();
        }

        public override AnimationCurve ReadJson(JsonReader reader, Type objectType, AnimationCurve existingValue, bool hasExistingValue, JsonSerializer serializer)
        {
            JToken token = JToken.Load(reader);
            var controlPoints = token.ToObject<List<List<float>>>();
            Keyframe[] keys = controlPoints.Select(pt => new Keyframe(pt[0], pt[1])).ToArray();

            var controlCurve = new AnimationCurve(keys);
            Utils.SmoothCurve(controlCurve);
            return controlCurve;
        }
    }

    public class VtbFacapConfigSerializationSettings : JsonSerializerSettings
    {
        public VtbFacapConfigSerializationSettings() : base()
        {
            this.Formatting = Formatting.Indented;
            this.Converters = new List<JsonConverter> { new VtbFacapConfigControlConverter() };
        }
    }
}
