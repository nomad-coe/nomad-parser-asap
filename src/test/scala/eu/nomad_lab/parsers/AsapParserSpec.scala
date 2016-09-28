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
  }
}
