package geotrellis.docs.demo

import javax.servlet.http.{HttpServletRequest}
import javax.ws.rs._
import javax.ws.rs.core.{Response, Context}

import geotrellis._
import geotrellis.data.{ColorBreaks,ColorRamps,ColorRamp}
import geotrellis.statistics.{Histogram}
import geotrellis.Implicits._

import geotrellis.raster.op._
import geotrellis.rest.op._
import geotrellis.statistics.op._
import geotrellis.Implicits._

import geotrellis.feature._

object response {
  def apply(mime:String)(data:Any) = Response.ok(data).`type`(mime).build()
  def error = Response.serverError().build()
}

@Path("/test") 
class TestService {
  @GET
  def get(@Context req:HttpServletRequest):Response = {
    response("text/plain")("It works!")
  }
}

@Path("/usace")
class Usace {
  @GET
  @Path("/{s}")
  def get(@PathParam("s") storage:String,
          @Context req:HttpServletRequest): Response = {
    val op = if(storage == "block") {
      io.LoadRaster("block_usace1") * 3 +
      io.LoadRaster("block_usace2") * 4 +
      io.LoadRaster("block_usace3") * 5
    } else {
      io.LoadRaster("local_usace1") * 3 +
      io.LoadRaster("local_usace2") * 4 +
      io.LoadRaster("local_usace3") * 5
    }

    try { 
      val startNanos = System.nanoTime()
      val img = Server.gt.run(op)
      val endNanos = System.nanoTime()
      val d = (endNanos - startNanos).toDouble
      response("text/plain")(s"Png rendered in: ${d/1000000} ms")
    } catch {
      case e:Throwable => response.error
    }    
  }

  @GET
  @Path("/{s}/{r}")
  def get(@PathParam("s") storage:String,
          @PathParam("r") respond:String,
          @Context req:HttpServletRequest): Response = {
    val resp = respond.toLowerCase != "false"
    val op = if(storage == "block") {
      io.LoadRaster("block_usace1") * 3 +
      io.LoadRaster("block_usace2") * 4 +
      io.LoadRaster("block_usace3") * 5
    } else {
      io.LoadRaster("local_usace1") * 3 +
      io.LoadRaster("local_usace2") * 4 +
      io.LoadRaster("local_usace3") * 5
    }

    val png = if (resp) io.SimpleRenderPng(op) else op
    try { 
      val startNanos = System.nanoTime()
      val img = Server.gt.run(png)
      val endNanos = System.nanoTime()
      val d = (endNanos - startNanos).toDouble
      if(resp)
        response("image/png")(img)
      else
        response("text/plain")(s"Png rendered in: ${d/1000000} ms")
    } catch {
      case e:Throwable => response.error
    }    

  }
}

@Path("/hillshade-con")
class HillShadeConcurrent {
 /** Runs a weighted overlay of a number of computed hillshades */
  def hillshade(r:String,rasts:Int = 1, resp:Boolean = true):Response = {
    val top = (1 to rasts).map { i => focal.Hillshade(io.LoadRaster(r)) * i }
                           .reduceLeft { (op1,op2) => (op1 + op2) }
    val op = local.Divide(top,(1 to rasts).sum)
    val png = io.SimpleRenderPng(op)
    try { 
      val startNanos = System.nanoTime()
      val img = Server.gt.run(png)
      val endNanos = System.nanoTime()
      val d = (endNanos - startNanos).toDouble
      if(resp)
        response("image/png")(img)
      else
        response("text/plain")(s"Png rendered in: ${d/1000000} ms")
    } catch {
      case e:Throwable => response.error
    }    
  }

  @GET
  def get(@Context req:HttpServletRequest):Response = 
    hillshade("rast1-small")
  
  @GET
  @Path("/{r}")
  def get(@PathParam("r") r:String,
          @Context req:HttpServletRequest):Response =
    hillshade(r)          

  @GET
  @Path("/{r}/{t}")
  def get(@PathParam("r") r:String,
          @PathParam("t") t:String,
          @Context req:HttpServletRequest):Response =
    hillshade(r,t.toInt)

  @GET
  @Path("/{r}/{t}/{response}")
  def get(@PathParam("r") r:String,
          @PathParam("t") t:String,
          @PathParam("response") response:String,
          @Context req:HttpServletRequest):Response =
    hillshade(r,t.toInt, response.toLowerCase != "false")
}

@Path("/hillshade") 
class HillShade {
   def hillshade(r:String,times:Int = 1,resp:Boolean = true):Response = {
    val rOp = io.LoadRaster(r)
    
    var op = focal.Hillshade(rOp)
    var i = 1
    while(i < times) { op = focal.Hillshade(op) ; i += 1 }
    
    
    val png = io.SimpleRenderPng(op)
    try { 
      val startNanos = System.nanoTime()
      val img = Server.gt.run(png)
      val endNanos = System.nanoTime()
      val d = (endNanos - startNanos).toDouble
      if(resp)
        response("image/png")(img)
      else
        response("text/plain")(s"Png rendered in: ${d/1000000} ms")
    } catch {
      case e:Throwable => response.error
    }
  }

  @GET
  def get(@Context req:HttpServletRequest):Response = 
    hillshade("rast1-small")
  
  @GET
  @Path("/{r}")
  def get(@PathParam("r") r:String,
          @Context req:HttpServletRequest):Response =
    hillshade(r)          

  @GET
  @Path("/{r}/{t}")
  def get(@PathParam("r") r:String,
          @PathParam("t") t:String,
          @Context req:HttpServletRequest):Response =
    hillshade(r,t.toInt)

  @GET
  @Path("/{r}/{t}/{response}")
  def get(@PathParam("r") r:String,
          @PathParam("t") t:String,
          @PathParam("response") response:String,
          @Context req:HttpServletRequest):Response =
    hillshade(r,t.toInt, response.toLowerCase != "false")
}

@Path("/wo") 
class WeightedOverlay {
  def weightedOverlay(r1:String,r2:String,w1:Int,w2:Int,resp:Boolean = true):Response = {
    val r1Op = io.LoadRaster(r1)
    val r2Op = io.LoadRaster(r2)

    val png = io.SimpleRenderPng( (r1Op*w1 + r2Op*w2) / w1+w2)

    try { 
      val startNanos = System.nanoTime()
      val img = Server.gt.run(png)
      val endNanos = System.nanoTime()
      val d = (endNanos - startNanos).toDouble
      if(resp)
        response("image/png")(img)
      else
        response("text/plain")(s"Png rendered in: ${d/1000000} ms")
    } catch {
      case e:Throwable => response.error
    }
  }

  @GET
  def get(@Context req:HttpServletRequest):Response = 
    weightedOverlay("rast1","rast2",2,1)
    
  @GET
  @Path("/{key}")
  def get(@PathParam("key") key:String,
          @Context req:HttpServletRequest):Response = {
    key match {
      case "big" =>
        weightedOverlay("rast1-big","rast2-big",2,1)
      case "no" =>
        weightedOverlay("rast1","rast2",2,1,false)        
      case "bigno" =>
        weightedOverlay("rast1-big","rast2-big",2,1,false)
      case _ =>
        get(req)
    }
  }

  @GET
  @Path("/{r1}/{r2}")
  def get(@PathParam("r1") r1:String,
          @PathParam("r2") r2:String,
          @Context req:HttpServletRequest):Response =
    weightedOverlay(r1,r2,1,2)

  @GET
  @Path("/{r1}/{r2}/{w1}/{w2}")
  def get(@PathParam("r1") r1:String,
          @PathParam("r2") r2:String,
          @PathParam("w1") w1:String,
          @PathParam("w2") w2:String,
          @Context req:HttpServletRequest):Response =
    weightedOverlay(r1,r2,w1.toInt,w2.toInt)

  @GET
  @Path("/{r1}/{r2}/{w1}/{w2}/{resp}")
  def get(@PathParam("r1") r1:String,
          @PathParam("r2") r2:String,
          @PathParam("w1") w1:String,
          @PathParam("w2") w2:String,
          @PathParam("resp") resp:String,
          @Context req:HttpServletRequest):Response =
            if(resp == "false")
              weightedOverlay(r1,r2,w1.toInt,w2.toInt,false)
            else
              weightedOverlay(r1,r2,w1.toInt,w2.toInt)              
}

@Path("/kerneldensity")
class KernelDensity {

  @GET
  @Path("extent/{extent}/features/{features}")
  def get(@PathParam("extent") extent:String,          // Map extent, in map units (left,bottom,right,top)
          @PathParam("features") features:String,     // String of point features (x1,y1,v1,x2,y2,v2,...)
          @QueryParam("callback") callback:String,     // Callback for JSON-P
          @Context req:HttpServletRequest):Response = {
    try {                               
      // Parse extent
      val extentArgs = extent.split(',')
      if(extentArgs.length != 4) { return Response.status(400).build() }
      val ext = Extent(extentArgs(0).toDouble,extentArgs(1).toDouble,extentArgs(2).toDouble,extentArgs(3).toDouble)

      val height = 150
      val width = (height * ((ext.xmax - ext.xmin) / (ext.ymax - ext.ymin))).toInt

      val cellWidth = (ext.xmax - ext.xmin) / width;
      val cellHeight = (ext.ymax - ext.ymin) / height;
      val rasterExtent = RasterExtent(ext,cellWidth,cellHeight,width,height);

      // Parse point features
      println(s"$features")
      val pointArgs = features.split(',')
      if(pointArgs.length == 0) { return Response.status(413).build() }
      
      val tup = scala.collection.mutable.ListBuffer[Double]()
      val points = scala.collection.mutable.ListBuffer[Point[Double]]()
      for(x <- pointArgs) {
        tup.append(x.toDouble)
        if(tup.length == 3) {
          points.append(Point(tup(0),tup(1),tup(2)))
          tup.clear()
        }
      }

      if(tup.length != 0) { return Response.status(416).build() }

      // Build he kernel density operation.
      val r = focal.KernelDensity(points, {x => x.toInt}:(Double=>Int), 
                                  focal.CreateGaussianRaster(75,75.0,6.7,200.0),rasterExtent)
                   .map(r=> r.map(v => if(v < 15.0) NODATA else v))

      // Create a range of colors based off of a default color ramp.
      val shades = 50
      val colors = stat.GetColorsFromPalette(ColorRamps.BlueToYellowToRed.colors,shades)
      
      // find the appropriate quantile class breaks to use for the delta
      val h = stat.GetHistogram(r)
      val breaks = stat.GetColorBreaks(h, colors)

      // render the png
      val png = io.RenderPng(r, breaks, h, 0)

      //Write the image, and return where it is.
      val imageUrl = Server.write(png)

      val result = s"""
        { 
          'url': '$imageUrl', 
          'width': '$width', 
          'height': '$height' 
        }"""

      response("text/javascript")(s"""$callback($result)""" )
    } catch {
      case e:Throwable => response("text/javascript")(e.toString)
    }
  }
}

@Path("/image") 
class ImageServer {
  @GET
  def get(@QueryParam("name") name:String,@Context req:HttpServletRequest) = {
    try {
      response("image/png")(Server.getImage(name))
    } catch {
      case e:Exception => response("text/plain")(s"$e\n\n${e.getStackTrace.toString}")
    }
  }
}
