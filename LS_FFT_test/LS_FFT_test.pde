import processing.net.*;
import processing.serial.*;
import org.apache.commons.lang3.*;

int fftcount = 20;
int[] fftchannel = new int[fftcount];
int[] fftrange = {0,255};
int vucount = 2;
float[] vumeter = new float[vucount];
int[] vurange = {0,180};
JSONObject DEBUG = new JSONObject();

// Network config
Client client;
String address = "localhost";
int netport = 57201;

// Serial config
boolean useSerial = false;
String portname = "/dev/ttys007";
int baud = 9600;
Serial port;

void setup() {
  size(200, 200);
  surface.setResizable(true);
  DEBUG.setBoolean("net",true);
  DEBUG.setBoolean("channel",false);
  surface.setSize((fftcount*50)+((fftcount+2)*10), 240);
  if (useSerial) {
    port = new Serial(this, portname, baud);
    println("Opened "+portname+" at "+baud+" baud");
  } else {
    client = new Client(this, address, netport);
    println("Opened "+address+":"+netport);
  }
}

void draw() {
  background(0);
  noStroke();
  for (int i=0; i<fftcount/2; i++) {
    fill((255-(float(i)/fftcount*512)), (float(i)/fftcount*512),0);
    rect((50*i)+(10*i)+10, 10+100-map(fftchannel[i],fftrange[0],fftrange[1], 0,100),
      50, map(fftchannel[i],fftrange[0],fftrange[1], 0,100));
  }
  for (int i=fftcount/2; i<fftcount; i++) {
   fill(0,(255-((float(i)/fftcount-0.5)*512)), ((float(i)/fftcount-0.5)*512));
   rect((50*i)+(10*i)+10, 10+100-map(fftchannel[i],fftrange[0],fftrange[1], 0,100),
     50, map(fftchannel[i],fftrange[0],fftrange[1], 0,100));
  }
  stroke(127);
  if (vumeter.length == 0) {
    line(80,230,10,230);
  } else {
    line(80,230,cos(-radians(180-(vumeter[0])))*70+80,sin(-radians(180-(vumeter[0])))*70+230);
  }
  if (!useSerial) {
    client.write("fr\0");
  }
}

void clientEvent(Client c) {
  String in = c.readStringUntil('\0');
  if (in != null) {
    try {
      JSONObject jso = JSONObject.parse(in);
      if (DEBUG.getBoolean("channel")) {
        println(jso);
      }
      int[] jscr = jso.getJSONArray("fftrange").getIntArray();
      if (jscr.length == 2) {
        fftrange = jscr;
      }
      int[] jsch = jso.getJSONArray("fftchannel").getIntArray(); 
      if (jsch.length >= fftcount) {
        fftchannel = jsch; 
      } else {
        int[] zeros = new int[fftcount-jsch.length];
        fftchannel = ArrayUtils.addAll(jsch,zeros);
      }
      int[] jsvu = jso.getJSONArray("vumeter").getIntArray();
      vumeter = new float[jsvu.length];
      for (int i=0; i<vumeter.length; i++) {
        vumeter[i] = jsvu[i];
      }
      int[] jsvr = jso.getJSONArray("vurange").getIntArray();
      if (jsvr.length == 2) {
        vurange = jsvr;
      }
      for (int i=0; i<vumeter.length; i++) {
        vumeter[i] = map(vumeter[i],vurange[0],vurange[1],0,180);
      }
      
    } catch (RuntimeException e) {
      e.printStackTrace();
    }
  }
}
void serialEvent(Serial p) {
  if (p.available() > fftcount) {
    for (int i=0; i<fftcount; i++) {
      fftchannel[i] = p.read();
    }
  }
}