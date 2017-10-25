/*
   Copyright 2016-2017 The NOMAD Developers Group

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
 */
package eu.nomad_lab.parsers

import org.specs2.mutable.Specification

object AsapParserSpec extends Specification {
  "AsapParserTest" >> {
    "test moldyn1 with json-events" >> {
      ParserRun.parse(AsapParser, "parsers/asap/test/examples/moldyn1.traj", "json-events") must_== ParseResult.ParseSuccess
    }
    "test moldyn1 with json" >> {
      ParserRun.parse(AsapParser, "parsers/asap/test/examples/moldyn1.traj", "json") must_== ParseResult.ParseSuccess
    }
    "test moldyn2 with json-events" >> {
      ParserRun.parse(AsapParser, "parsers/asap/test/examples/moldyn2.traj", "json-events") must_== ParseResult.ParseSuccess
    }
    "test moldyn2 with json" >> {
      ParserRun.parse(AsapParser, "parsers/asap/test/examples/moldyn2.traj", "json") must_== ParseResult.ParseSuccess
    }
    "test geo_opt1 with json-events" >> {
      ParserRun.parse(AsapParser, "parsers/asap/test/examples/geo_opt1.traj", "json-events") must_== ParseResult.ParseSuccess
    }
    "test geo_opt1 with json" >> {
      ParserRun.parse(AsapParser, "parsers/asap/test/examples/geo_opt1.traj", "json") must_== ParseResult.ParseSuccess
    }
  }
}
