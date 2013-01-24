package geotrellis.docs.demo

import geotrellis._
import geotrellis.process.{Server => TrellisServer}

object Server {
  val gt = TrellisServer("demo-handler", "data/catalog.json")

  def write(op:Op[Array[Byte]]):String = {
    val bytes = gt.run(op)
    val name = System.currentTimeMillis / 1000
    val os = new java.io.FileOutputStream(s"/png/$name.png")
    try {  
      os.write(gt.run(op));  
    } finally {  
      os.close();  
    }
    s"http://localhost:8000/image?name=$name"
  }

  def getImage(name:String):Array[Byte] = {
    val is = new java.io.FileInputStream(s"/png/$name.png")
    val cnt = is.available
    val bytes = Array.ofDim[Byte](cnt)
    is.read(bytes)
    is.close()
    bytes
  }
}
