package geotrellis.benchmark.oldfocal

import geotrellis._
import geotrellis.raster._
import geotrellis.statistics._

case class Mode(r:Op[Raster], neighborhoodType: Neighborhood) extends Op1(r)({
  r => FocalOp.getResultInt(r, Default, neighborhoodType, () => new ModeCalc)
})

class ModeCalc extends FocalCalculation[Int] {
  var h:Histogram = FastMapHistogram()
  def clear() { h = FastMapHistogram() }
  def add(col:Int, row:Int, r:Raster) { h.countItem(r.get(col, row), 1) }
  def remove(col:Int, row:Int, r:Raster) { h.countItem(r.get(col, row), -1) }
  def getResult = h.getMode
}
