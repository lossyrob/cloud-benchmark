package geotrellis.benchmark

/*
 * # Caliper API key for jmarcus@azavea.com
 * postUrl: http://microbenchmarks.appspot.com:80/run/
 * apiKey: 3226081d-9776-40f4-a2d7-a1dc99c948c6
*/

import geotrellis._
import geotrellis.Implicits._
import geotrellis.data._
import geotrellis.data.png._
import geotrellis.raster.op._
import geotrellis.io._
import geotrellis.raster.op.focal.Normalize
import geotrellis.process._
import geotrellis.raster._
import geotrellis.statistics._
import geotrellis.raster.op.local._
import geotrellis.raster.op.tiles._
import geotrellis.statistics.op._
import geotrellis.raster.op.extent.GetRasterExtent
import geotrellis.statistics.op.stat.GetHistogram

import com.google.caliper.Benchmark
import com.google.caliper.Param
import com.google.caliper.Runner 
import com.google.caliper.SimpleBenchmark

import scala.math.{min, max}
import scala.util.Random

abstract class BenchmarkRunner(cls:java.lang.Class[_ <: Benchmark]) {
  def main(args:Array[String]): Unit = Runner.main(cls, args:_*)
}

object DataMap extends BenchmarkRunner(classOf[DataMap])
class DataMap extends SimpleBenchmark {
  var server:Server = null

  @Param(Array("2048"))
  var size:Int = 0

  var ints:Array[Int] = null
  var doubles:Array[Double] = null
  var raster:Raster = null
  var bitData:BitArrayRasterData = null
  var byteData:ByteArrayRasterData = null
  var shortData:ShortArrayRasterData = null

  /**
   * Sugar to run 'f' for 'reps' number of times.
   */
  def run(reps:Int)(f: => Unit) = {
    var i = 0
    while (i < reps) { f; i += 1 }
  }

  /**
   * Sugar for building arrays using a per-cell init function.
   */
  def init[A:Manifest](size:Int)(init: => A) = {
    val data = Array.ofDim[A](size)
    for (i <- 0 until size) data(i) = init
    data
  }

  override def setUp() {
    server = Server("benchmark", Catalog.empty("benchmark"))
    val len = size * size
    ints = init(len)(Random.nextInt)
    doubles = init(len)(Random.nextDouble)
    val re = RasterExtent(Extent(0, 0, size, size), 1.0, 1.0, size, size)
    raster = Raster(init(len)(Random.nextInt), re)

    bitData = new BitArrayRasterData(init((len + 7) / 8)(Random.nextInt.toByte), size, size)
    byteData = new ByteArrayRasterData(init(len)(Random.nextInt.toByte), size, size)
    shortData = new ShortArrayRasterData(init(len)(Random.nextInt.toShort), size, size)
  }

  def timeIntArrayWhileLoop(reps:Int) = run(reps)(intArrayWhileLoop)
  def intArrayWhileLoop = {
    val goal = ints.clone
    var i = 0
    val len = goal.length
    while (i < len) {
      val z = goal(i)
      if (z != NODATA) goal(i) = z * 2
      i += 1
    }
    goal
  }
  
  def timeDoubleArrayWhileLoop(reps:Int) = run(reps)(doubleArrayWhileLoop)
  def doubleArrayWhileLoop = {
    val goal = doubles.clone
    var i = 0
    val len = goal.length
    while (i < len) {
      val z = goal(i)
      if (z != NODATA) goal(i) = z * 2.0
      i += 1
    }
    goal
  }
  
  def timeRasterWhileLoop(reps:Int) = run(reps)(rasterWhileLoop)
  def rasterWhileLoop = {
    val rcopy = raster.copy
    val goal = rcopy.data.mutable.getOrElse(sys.error("argh"))

    var i = 0
    val len = goal.length
    while (i < len) {
      val z = goal(i)
      if (z != NODATA) goal(i) = goal(i) * 2
      i += 1
    }
    rcopy
  }
  
  def timeRasterMap(reps:Int) = run(reps)(rasterMap)
  def rasterMap = raster.map(z => if (z != NODATA) z * 2 else NODATA)

  def timeRasterMapIfSet(reps:Int) = run(reps)(rasterMapIfSet)
  def rasterMapIfSet = raster.mapIfSet(z => z * 2)

  def timeBitDataWhileLoop(reps:Int) = run(reps)(bitDataWhileLoop)
  def bitDataWhileLoop = {
    val data = bitData.copy
    var i = 0
    val len = data.length
    while (i < len) {
      val z = data(i)
      if (z != NODATA) data(i) = data(i) * 2
      i += 1
    }
    data
  }

  def timeBitDataMap(reps:Int) = run(reps)(bitDataMap)
  def bitDataMap = bitData.map(z => if (z != NODATA) z * 2 else NODATA)

  def timeByteDataWhileLoop(reps:Int) = run(reps)(byteDataWhileLoop)
  def byteDataWhileLoop = {
    val data = byteData.copy
    var i = 0
    val len = data.length
    while (i < len) {
      val z = data(i)
      if (z != NODATA) data(i) = data(i) * 2
      i += 1
    }
    data
  }
  
  def timeByteDataMap(reps:Int) = run(reps)(byteDataMap)
  def byteDataMap = byteData.map(z => if (z != NODATA) z * 2 else NODATA)

  def timeShortDataWhileLoop(reps:Int) = run(reps)(shortDataWhileLoop)
  def shortDataWhileLoop = {
    val data = shortData.copy
    var i = 0
    val len = data.length
    while (i < len) {
      val z = data(i)
      if (z != NODATA) data(i) = data(i) * 2
      i += 1
    }
    data
  }
  
  def timeShortDataMap(reps:Int) = run(reps)(shortDataMap)
  def shortDataMap = shortData.map(z => if (z != NODATA) z * 2 else NODATA)
}

object Usace {
 // def main(args:Array[String]) = {
 //   println("Creating server...")
 //   val catalog = Catalog.fromPath("./data/catalog.json")
 //   val server = Server("usace", catalog)

 //   println("Running local...")
 //   var startNanos = System.nanoTime()
 //   runLocal(server)
 //   var endNanos = System.nanoTime()
 //   println("done.")
 //   val local = endNanos - startNanos 

 //   println("Running single standard...")
 //   startNanos = System.nanoTime()
 //   runSingleStandard(server)
 //   endNanos = System.nanoTime()
 //   println("done.")
 //   val singleStandard = endNanos - startNanos 

 //   println("Running single provisioned...")
 //   startNanos = System.nanoTime()
 //   runSingleProvisioned(server)
 //   endNanos = System.nanoTime()
 //   println("done.")
 //   val singleProvisioned = endNanos - startNanos 

 //   println("Running raid standard...")
 //   startNanos = System.nanoTime()
 //   runRaidStandard(server)
 //   endNanos = System.nanoTime()
 //   println("done.")
 //   val raidStandard = endNanos - startNanos 

 //   println("Running raid provisioned...")
 //   startNanos = System.nanoTime()
 //   runRaidProvisioned(server)
 //   endNanos = System.nanoTime()
 //   println("done.")
 //   val raidProvisioned = endNanos - startNanos 
   
 //   println("[FINISHED]")
 //   println(s"[LOCAL] ${local/1000000}")
 //   println(s"[SINGLE-STANDARD] ${singleStandard/1000000}")
 //   println(s"[SINGLE-PROVISIONED] ${singleProvisioned/1000000}")
 //   println(s"[RAID-STANDARD] ${raidStandard/1000000}")
 //   println(s"[RAID-PROVISIONED] ${raidProvisioned/1000000}")
 //   println(s"[CSV] ${local/1000000},${singleStandard/1000000},${singleProvisioned/1000000},${raidStandard/1000000},${raidProvisioned/1000000}")
 //   server.shutdown()
 // }

  def runLocal(server:Server) = {
    val r1 = io.LoadRaster("local-r1")
    val r2 = io.LoadRaster("local-r2")
    val r3 = io.LoadRaster("local-r3")

    val op = r1 * 3 + r2 * 2 + r3 * 5
    server.run(op)
  }

  def runSingleStandard(server:Server) = {
    val r1 = io.LoadRaster("single-standard-r1")
    val r2 = io.LoadRaster("single-standard-r2")
    val r3 = io.LoadRaster("single-standard-r3")

    val op = r1 * 3 + r2 * 2 + r3 * 5
    server.run(op)
  }

  def runSingleProvisioned(server:Server) = {
    val r1 = io.LoadRaster("single-provisioned-r1")
    val r2 = io.LoadRaster("single-provisioned-r2")
    val r3 = io.LoadRaster("single-provisioned-r3")

    val op = r1 * 3 + r2 * 2 + r3 * 5
    server.run(op)
  }

  def runRaidStandard(server:Server) = {
    val r1 = io.LoadRaster("raid-standard-r1")
    val r2 = io.LoadRaster("raid-standard-r2")
    val r3 = io.LoadRaster("raid-standard-r3")

    val op = r1 * 3 + r2 * 2 + r3 * 5
    server.run(op)
  }

  def runRaidProvisioned(server:Server) = {
    val r1 = io.LoadRaster("raid-provisioned-r1")
    val r2 = io.LoadRaster("raid-provisioned-r2")
    val r3 = io.LoadRaster("raid-provisioned-r3")

    val op = r1 * 3 + r2 * 2 + r3 * 5
    server.run(op)
  }
}

