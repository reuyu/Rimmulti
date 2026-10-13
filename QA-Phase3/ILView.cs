using System;
using System.Reflection;
using System.Reflection.Emit;
using System.Collections.Generic;
using System.Text;
public static class QaIL {
 static Dictionary<ushort,OpCode> ops=new Dictionary<ushort,OpCode>();
 static QaIL(){foreach(var f in typeof(OpCodes).GetFields(BindingFlags.Public|BindingFlags.Static)){if(f.FieldType==typeof(OpCode)){var op=(OpCode)f.GetValue(null);ops[unchecked((ushort)op.Value)]=op;}}}
 public static string Dump(MethodBase m){var sb=new StringBuilder();sb.AppendLine(m.DeclaringType+"::"+m);var b=m.GetMethodBody()?.GetILAsByteArray();if(b==null)return sb.ToString();int i=0;while(i<b.Length){int start=i;ushort v=b[i++];if(v==254)v=(ushort)(0xfe00|b[i++]);var o=ops[v];object arg="";int n=0;switch(o.OperandType){
 case OperandType.InlineNone:break;
 case OperandType.ShortInlineI:arg=(sbyte)b[i];n=1;break;
 case OperandType.ShortInlineVar:arg=b[i];n=1;break;
 case OperandType.InlineVar:arg=BitConverter.ToUInt16(b,i);n=2;break;
 case OperandType.ShortInlineBrTarget:arg="IL_"+(i+1+(sbyte)b[i]).ToString("x4");n=1;break;
 case OperandType.InlineBrTarget:arg="IL_"+(i+4+BitConverter.ToInt32(b,i)).ToString("x4");n=4;break;
 case OperandType.InlineI:arg=BitConverter.ToInt32(b,i);n=4;break;
 case OperandType.InlineI8:arg=BitConverter.ToInt64(b,i);n=8;break;
 case OperandType.ShortInlineR:arg=BitConverter.ToSingle(b,i);n=4;break;
 case OperandType.InlineR:arg=BitConverter.ToDouble(b,i);n=8;break;
 case OperandType.InlineSwitch:int c=BitConverter.ToInt32(b,i);n=4+c*4;arg="switch "+c;break;
 default:int tok=BitConverter.ToInt32(b,i);n=4;try{arg=o.OperandType==OperandType.InlineString?(object)m.Module.ResolveString(tok):m.Module.ResolveMember(tok);}catch{arg="token:"+tok.ToString("x8");}break;}
 i+=n;sb.AppendLine($"{start:x4}: {o.Name} {arg}");}return sb.ToString();}
}
