import sbt._
import sbt.Keys._

object DemoBuild extends Build {
  val key = AttributeKey[Boolean]("javaOptionsPatched")
  
  fork in run := true

  lazy val root = Project("root", file(".")).settings(
    javaOptions in run += "-Xmx5G"
  )
}
