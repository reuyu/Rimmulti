// Logic-only adapters. These do not validate Unity rendering or engine callbacks.
namespace UnityEngine {
 public struct Vector2 { public Vector2(float x,float y) {} }
 public struct Rect { public float width,height; public Rect(float x,float y,float w,float h) {width=w;height=h;} }
}
namespace Verse {
 public class Window {
  public bool forcePause,doCloseX,closeOnClickedOutside,absorbInputAroundWindow;
  public int CloseCalls;
  public virtual UnityEngine.Vector2 InitialSize=>default;
  public virtual void DoWindowContents(UnityEngine.Rect rect) {}
  public void Close() { CloseCalls++; PreClose(); }
  public virtual void PreClose() {}
 }
 public enum GameFont {Small,Medium}
 public static class Text {public static GameFont Font;}
 public static class Widgets {
  public static void Label(UnityEngine.Rect rect,string text) {}
  public static bool ButtonText(UnityEngine.Rect rect,string text)=>false;
 }
 public static class Messages {
  public static readonly List<string> Values=new();
  public static void Message(string text,object type,bool historical) {Values.Add(text);}
 }
}
namespace RimWorld {public static class MessageTypeDefOf {
 public static readonly object NeutralEvent=new(),PositiveEvent=new(),RejectInput=new();
}}
namespace WarEconomy.Client.Networking {public class NetworkClient {
 public static readonly NetworkClient Instance=new();
 public readonly List<WarEconomy.Common.Packets.IPacket> Sent=new();
 public void SendPacket<T>(T packet) where T:WarEconomy.Common.Packets.IPacket {Sent.Add(packet);}
}}
