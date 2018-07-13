/*
 * Copyright 2016-2018 Mikkel Strange, Fawzi Mohamed
 * 
 *   Licensed under the Apache License, Version 2.0 (the "License");
 *   you may not use this file except in compliance with the License.
 *   You may obtain a copy of the License at
 * 
 *     http://www.apache.org/licenses/LICENSE-2.0
 * 
 *   Unless required by applicable law or agreed to in writing, software
 *   distributed under the License is distributed on an "AS IS" BASIS,
 *   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *   See the License for the specific language governing permissions and
 *   limitations under the License.
 */

package eu.nomad_lab.parsers

import eu.{ nomad_lab => lab }
import eu.nomad_lab.DefaultPythonInterpreter
import org.{ json4s => jn }
import scala.collection.breakOut
import java.nio.charset.StandardCharsets

object AsapParser extends SimpleExternalParserGenerator(
  name = "AsapParser",
  parserInfo = jn.JObject(
    ("name" -> jn.JString("AsapParser")) ::
      ("parserId" -> jn.JString("AsapParser" + lab.AsapVersionInfo.version)) ::
      ("versionInfo" -> jn.JObject(
        ("nomadCoreVersion" -> jn.JObject(lab.NomadCoreVersionInfo.toMap.map {
          case (k, v) => k -> jn.JString(v.toString)
        }(breakOut): List[(String, jn.JString)])) ::
          (lab.AsapVersionInfo.toMap.map {
            case (key, value) =>
              (key -> jn.JString(value.toString))
          }(breakOut): List[(String, jn.JString)])
      )) :: Nil
  ),
  mainFileTypes = Seq("application/octet-stream"),
  cmd = Seq(DefaultPythonInterpreter.pythonExe(), "${envDir}/parsers/asap/parser/parser-asap/parser_asap.py",
    "${mainFilePath}"),
  mainFileRe = "".r,
  resList = Seq(
    "parser-asap/setup_paths.py",
    "parser-asap/parser_asap.py",
    "parser-asap/constraint_conversion.py",
    "nomad_meta_info/public.nomadmetainfo.json",
    "nomad_meta_info/common.nomadmetainfo.json",
    "nomad_meta_info/meta_types.nomadmetainfo.json",
    "nomad_meta_info/asap.nomadmetainfo.json"
  ) ++ DefaultPythonInterpreter.commonFiles(),
  dirMap = Map(
    "parser-asap" -> "parsers/asap/parser/parser-asap",
    "nomad_meta_info" -> "nomad-meta-info/meta_info/nomad_meta_info"
  ) ++ DefaultPythonInterpreter.commonDirMapping(),
  metaInfoEnv = Some(lab.meta.KnownMetaInfoEnvs.asap)
) {
  override def isMainFile(filePath: String, bytePrefix: Array[Byte], stringPrefix: Option[String]): Option[ParserMatch] = {
    if (bytePrefix.startsWith("AFFormatASE-Trajectory".getBytes(StandardCharsets.US_ASCII)))
      Some(ParserMatch(mainFileMatchPriority, mainFileMatchWeak))
    else
      None
  }
}
