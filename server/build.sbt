import AssemblyKeys._

name := "GeoTrellis benchmark services"

scalaVersion := "2.10.0"

scalacOptions ++= Seq(
              "-deprecation", 
              "-optimize", 
              "-unchecked", 
              "-language:implicitConversions", 
              "-language:postfixOps", 
              "-language:existentials", 
              "-feature")

libraryDependencies ++= Seq("org.scala-lang" % "scala-reflect" % "2.10.0",
                            "com.typesafe.akka" %% "akka-kernel" % "2.1.0",
                            "com.typesafe.akka" %% "akka-remote" % "2.1.0",
                            "com.typesafe.akka" %% "akka-actor" % "2.1.0",
                            "org.eclipse.jetty" % "jetty-webapp" % "8.1.0.RC4",
                            "asm" % "asm" % "3.3.1",
                            "com.sun.jersey" % "jersey-bundle" % "1.11"
)

resolvers ++= Seq(
          "sonatypeSnapshots" at "http://oss.sonatype.org/content/repositories/snapshots",
          "maven2 dev repository" at "http://download.java.net/maven/2")

assemblySettings

mergeStrategy in assembly <<= (mergeStrategy in assembly) {
  (old) => {
    case "application.conf" => MergeStrategy.concat
    case "META-INF/MANIFEST.MF" => MergeStrategy.discard
    case "META-INF\\MANIFEST.MF" => MergeStrategy.discard
    case "reference.conf" => MergeStrategy.concat   
    case _ => MergeStrategy.first
  }
}
