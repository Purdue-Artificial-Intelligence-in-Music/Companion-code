// External file used in ScoreDisplay.tsx to display the mapped score's content visually
// key (string) = score's name
// value (string) = score's XML file 
const scoresData: Record<string, string> = {
    "air_on_the_g_string.musicxml": `<?xml version="1.0" encoding="UTF-8"?>
  <score-partwise version="3.1">
    <work>
    <work-title>Air VLC Duet</work-title>
  </work>
  <movement-title>air_on_the_g_string.musicxml</movement-title>
  <identification>
    <creator type="composer">Bach</creator>
    <encoding>
      <encoding-date>2024-09-11</encoding-date>
      <software>music21 v.8.3.0</software>
      <software>MuseScore 3.6.2</software>
      <supports attribute="new-system" element="print" type="yes" value="yes" />
      <supports attribute="new-page" element="print" type="yes" value="yes" />
    </encoding>
  </identification>
  <defaults>
    <scaling>
      <millimeters>6.99912</millimeters>
      <tenths>40</tenths>
    </scaling>
    <page-layout>
      <page-height>1696.93</page-height>
      <page-width>1200.48</page-width>
      <page-margins>
        <left-margin>85.7251</left-margin>
        <right-margin>85.7251</right-margin>
        <top-margin>85.7251</top-margin>
        <bottom-margin>85.7251</bottom-margin>
      </page-margins>
    </page-layout>
    <word-font font-family="Edwin" font-size="10" />
    <lyric-font font-family="Edwin" font-size="10" />
  </defaults>
  <credit page="1">
    <credit-words default-x="600.241" default-y="1611.21" font-size="22" justify="center" valign="top">Air on the G String</credit-words>
  </credit>
  <credit page="1">
    <credit-words default-x="1114.76" default-y="1511.21" justify="right" valign="bottom">J.S. Bach</credit-words>
  </credit>
  <part-list>
    <part-group number="1" type="start">
      <group-symbol>bracket</group-symbol>
      <group-barline>yes</group-barline>
    </part-group>
    <part-group number="2" type="start">
      <group-symbol>square</group-symbol>
      <group-barline>yes</group-barline>
    </part-group>
    <score-part id="P1">
      <part-name>Violoncello 1</part-name>
      <part-abbreviation>Vc. 1</part-abbreviation>
      <score-instrument id="Iabcb343b378041048a64021b8c1b20d5">
        <instrument-name>Violoncello</instrument-name>
        <instrument-abbreviation>Vc</instrument-abbreviation>
      </score-instrument>
      <midi-instrument id="Iabcb343b378041048a64021b8c1b20d5">
        <midi-channel>1</midi-channel>
        <midi-program>43</midi-program>
      </midi-instrument>
    </score-part>
    <score-part id="P2">
      <part-name>Violoncello 2</part-name>
      <part-abbreviation>Vc. 2</part-abbreviation>
      <score-instrument id="I8d2924203d240686d6ea2c2f35084e83">
        <instrument-name>Violoncello</instrument-name>
        <instrument-abbreviation>Vc</instrument-abbreviation>
      </score-instrument>
      <midi-instrument id="I8d2924203d240686d6ea2c2f35084e83">
        <midi-channel>4</midi-channel>
        <midi-program>43</midi-program>
      </midi-instrument>
    </score-part>
    <part-group number="1" type="stop" />
    <part-group number="2" type="stop" />
  </part-list>
  <!--=========================== Part 1 ===========================-->
  <part id="P1">
    <!--========================= Measure 1 ==========================-->
    <measure number="1" width="264">
      <print>
        <system-layout>
          <system-margins>
            <left-margin>141.84</left-margin>
            <right-margin>0</right-margin>
          </system-margins>
          <top-system-distance>170</top-system-distance>
        </system-layout>
      </print>
      <attributes>
        <divisions>10080</divisions>
        <key>
          <fifths>3</fifths>
        </key>
        <time>
          <beats>4</beats>
          <beat-type>4</beat-type>
        </time>
        <clef>
          <sign>F</sign>
          <line>4</line>
        </clef>
      </attributes>
      <direction placement="above">
        <direction-type>
          <metronome parentheses="no">
            <beat-unit>quarter</beat-unit>
            <per-minute>100</per-minute>
          </metronome>
        </direction-type>
        <sound tempo="100" />
      </direction>
      <direction placement="below">
        <direction-type>
          <dynamics default-x="6.5" default-y="-40" relative-y="-25">
            <mf />
          </dynamics>
        </direction-type>
        <sound dynamics="69" />
      </direction>
      <note default-x="123.23" default-y="10">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>40320</duration>
        <tie type="start" />
        <type>whole</type>
        <notations>
          <tied type="start" />
        </notations>
      </note>
    </measure>
    <!--========================= Measure 2 ==========================-->
    <measure number="2" width="157.27">
      <note default-x="16.5" default-y="10">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>40320</duration>
        <tie type="stop" />
        <tie type="start" />
        <type>whole</type>
        <notations>
          <tied type="stop" />
          <tied type="start" />
        </notations>
      </note>
    </measure>
    <!--========================= Measure 3 ==========================-->
    <measure number="3" width="264.18">
      <note default-x="16.5" default-y="10">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>10080</duration>
        <tie type="stop" />
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <tied type="stop" />
        </notations>
      </note>
      <note default-x="68.26" default-y="25">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="1" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="100.62" default-y="15">
        <pitch>
          <step>D</step>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="1" type="stop" />
        </notations>
      </note>
      <note default-x="132.97" default-y="5">
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="2" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="165.32" default-y="0">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
      </note>
      <note default-x="197.67" default-y="-5">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
      </note>
      <note default-x="230.02" default-y="0">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="2" type="stop" />
        </notations>
      </note>
    </measure>
    <!--========================= Measure 4 ==========================-->
    <measure number="4" width="201.42">
      <note default-x="16.5" default-y="-5">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>20160</duration>
        <type>half</type>
        <stem>down</stem>
      </note>
      <note default-x="102.67" default-y="-10">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <notations>
          <slur number="3" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="129.6" default-y="-15">
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>15120</duration>
        <type>quarter</type>
        <dot />
        <stem>down</stem>
        <notations>
          <slur number="3" type="stop" />
        </notations>
      </note>
    </measure>
    <!--========================= Measure 5 ==========================-->
    <measure number="5" width="307.15">
      <print new-system="yes">
        <system-layout>
          <system-margins>
            <left-margin>68.85</left-margin>
            <right-margin>0</right-margin>
          </system-margins>
          <system-distance>105.03</system-distance>
        </system-layout>
      </print>
      <note default-x="103.65" default-y="20">
        <pitch>
          <step>E</step>
          <octave>4</octave>
        </pitch>
        <duration>40320</duration>
        <type>whole</type>
        <notations>
          <slur number="4" placement="above" type="start" />
          <slur number="5" placement="above" type="start" />
        </notations>
      </note>
    </measure>
    <!--========================= Measure 6 ==========================-->
    <measure number="6" width="393.47">
      <note default-x="20.96" default-y="20">
        <pitch>
          <step>E</step>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="4" type="stop" />
        </notations>
      </note>
      <note default-x="67.3" default-y="10">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
        <notations>
          <slur number="5" type="stop" />
        </notations>
      </note>
      <note default-x="113.64" default-y="-5">
        <pitch>
          <step>G</step>
          <alter>0</alter>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <accidental>natural</accidental>
        <stem>down</stem>
        <beam number="1">continue</beam>
        <notations>
          <slur number="6" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="159.98" default-y="-10">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="6" type="stop" />
        </notations>
      </note>
      <note default-x="206.32" default-y="5">
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="1" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="252.65" default-y="0">
        <pitch>
          <step>A</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <accidental>sharp</accidental>
        <stem>down</stem>
        <beam number="1">continue</beam>
        <notations>
          <slur number="1" type="stop" />
        </notations>
      </note>
      <note default-x="298.99" default-y="20">
        <pitch>
          <step>E</step>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
        <notations>
          <slur number="2" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="345.33" default-y="15">
        <pitch>
          <step>D</step>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="2" type="stop" />
        </notations>
      </note>
    </measure>
    <!--========================= Measure 7 ==========================-->
    <measure number="7" width="259.23">
      <note default-x="16.5" default-y="15">
        <pitch>
          <step>D</step>
          <octave>4</octave>
        </pitch>
        <duration>40320</duration>
        <type>whole</type>
        <notations>
          <slur number="3" placement="above" type="start" />
          <slur number="4" placement="above" type="start" />
        </notations>
      </note>
    </measure>
    <!--========================= Measure 8 ==========================-->
    <measure number="8" width="403.01">
      <print new-system="yes">
        <system-layout>
          <system-margins>
            <left-margin>68.85</left-margin>
            <right-margin>0</right-margin>
          </system-margins>
          <system-distance>105.03</system-distance>
        </system-layout>
      </print>
      <note default-x="101.11" default-y="15">
        <pitch>
          <step>D</step>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="3" type="stop" />
        </notations>
      </note>
      <note default-x="138.62" default-y="5">
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
        <notations>
          <slur number="4" type="stop" />
        </notations>
      </note>
      <note default-x="176.13" default-y="-10">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
        <notations>
          <slur number="5" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="213.65" default-y="-15">
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="5" type="stop" />
        </notations>
      </note>
      <note default-x="251.16" default-y="0">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="6" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="288.67" default-y="-5">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
        <notations>
          <slur number="6" type="stop" />
        </notations>
      </note>
      <note default-x="326.19" default-y="15">
        <pitch>
          <step>D</step>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
        <notations>
          <slur number="1" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="363.7" default-y="10">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="1" type="stop" />
        </notations>
      </note>
    </measure>
    <!--========================= Measure 9 ==========================-->
    <measure number="9" width="235.97">
      <note default-x="16.5" default-y="10">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>30240</duration>
        <type>half</type>
        <dot />
        <stem>down</stem>
      </note>
      <note default-x="170.15" default-y="15">
        <pitch>
          <step>D</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <accidental>sharp</accidental>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="2" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="202.16" default-y="20">
        <pitch>
          <step>E</step>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="2" type="stop" />
        </notations>
      </note>
    </measure>
    <!--========================= Measure 10 =========================-->
    <measure number="10" width="320.86">
      <note default-x="13" default-y="0">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="68.19" default-y="0">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>2520</duration>
        <type>16th</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <beam number="2">begin</beam>
        <notations>
          <slur number="3" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="93.28" default-y="5">
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>2520</duration>
        <type>16th</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
        <beam number="2">end</beam>
      </note>
      <note default-x="118.36" default-y="10">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="4" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="158.5" default-y="10">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="4" type="stop" />
        </notations>
      </note>
      <note default-x="198.64" default-y="5">
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
        <notations>
          <slur number="3" type="stop" />
        </notations>
      </note>
      <note default-x="238.78" default-y="5">
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
        <notations>
          <slur number="5" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="278.92" default-y="0">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="5" type="stop" />
        </notations>
      </note>
    </measure>
    <!--========================= Measure 11 =========================-->
    <measure number="11" width="372.26">
      <print new-system="yes">
        <system-layout>
          <system-margins>
            <left-margin>68.85</left-margin>
            <right-margin>0</right-margin>
          </system-margins>
          <system-distance>105.03</system-distance>
        </system-layout>
      </print>
      <note default-x="101.11" default-y="-5">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="6" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="136.43" default-y="-10">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="6" type="stop" />
        </notations>
      </note>
      <note default-x="171.76" default-y="-10">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>2520</duration>
        <type>16th</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <beam number="2">begin</beam>
        <notations>
          <slur number="1" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="193.84" default-y="-5">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>2520</duration>
        <type>16th</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
        <beam number="2">end</beam>
      </note>
      <note default-x="215.91" default-y="0">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="2" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="251.24" default-y="0">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur number="1" type="stop" />
          <slur number="2" type="stop" />
        </notations>
      </note>
      <note default-x="299.81" default-y="-5">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="3" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="335.14" default-y="-10">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="3" type="stop" />
        </notations>
      </note>
    </measure>
    <!--========================= Measure 12 =========================-->
    <measure number="12" width="114.24">
      <note default-x="16.5" default-y="-15">
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>40320</duration>
        <type>whole</type>
      </note>
    </measure>
    <!--========================= Measure 13 =========================-->
    <measure number="13" width="287.66">
      <note default-x="16.5" default-y="-5">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>20160</duration>
        <type>half</type>
        <stem>down</stem>
        <notations>
          <slur number="4" placement="above" type="start" />
          <slur number="5" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="118.67" default-y="-5">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="4" type="stop" />
        </notations>
      </note>
      <note default-x="155.82" default-y="0">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>2520</duration>
        <type>16th</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
        <beam number="2">begin</beam>
      </note>
      <note default-x="179.04" default-y="-5">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>2520</duration>
        <type>16th</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <beam number="2">end</beam>
      </note>
      <note default-x="202.26" default-y="-10">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>2520</duration>
        <type>16th</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <beam number="2">begin</beam>
      </note>
      <note default-x="225.48" default-y="-5">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>2520</duration>
        <type>16th</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
        <beam number="2">end</beam>
      </note>
      <note default-x="248.71" default-y="-15">
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="5" type="stop" />
        </notations>
      </note>
    </measure>
    <!--========================= Measure 14 =========================-->
    <measure number="14" width="185.68">
      <note default-x="16.5" default-y="20">
        <pitch>
          <step>E</step>
          <octave>4</octave>
        </pitch>
        <duration>30240</duration>
        <type>half</type>
        <dot />
        <stem>down</stem>
      </note>
      <note default-x="142.03" default-y="-5">
        <pitch>
          <step>G</step>
          <alter>0</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <accidental>natural</accidental>
        <stem>down</stem>
        <notations>
          <slur number="6" placement="above" type="start" />
        </notations>
      </note>
    </measure>
    <!--========================= Measure 15 =========================-->
    <measure number="15" width="401.68">
      <print new-system="yes">
        <system-layout>
          <system-margins>
            <left-margin>68.85</left-margin>
            <right-margin>0</right-margin>
          </system-margins>
          <system-distance>105.03</system-distance>
        </system-layout>
      </print>
      <note default-x="113.37" default-y="-10">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur number="6" type="stop" />
        </notations>
      </note>
      <note default-x="177.03" default-y="25">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur number="1" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="240.7" default-y="25">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="1" type="stop" />
        </notations>
      </note>
      <note default-x="280.5" default-y="20">
        <pitch>
          <step>E</step>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
        <notations>
          <slur number="2" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="320.29" default-y="15">
        <pitch>
          <step>D</step>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
      </note>
      <note default-x="360.08" default-y="10">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="2" type="stop" />
        </notations>
      </note>
    </measure>
    <!--========================= Measure 16 =========================-->
    <measure number="16" width="321.08">
      <note default-x="16.5" default-y="15">
        <pitch>
          <step>D</step>
          <octave>4</octave>
        </pitch>
        <duration>20160</duration>
        <type>half</type>
        <stem>down</stem>
        <notations>
          <slur number="3" placement="above" type="start" />
          <slur number="4" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="131.35" default-y="15">
        <pitch>
          <step>D</step>
          <octave>4</octave>
        </pitch>
        <duration>2520</duration>
        <type>16th</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <beam number="2">begin</beam>
        <notations>
          <slur number="3" type="stop" />
        </notations>
      </note>
      <note default-x="157.45" default-y="10">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>2520</duration>
        <type>16th</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
        <beam number="2">continue</beam>
      </note>
      <note default-x="183.55" default-y="5">
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>2520</duration>
        <type>16th</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
        <beam number="2">continue</beam>
      </note>
      <note default-x="209.65" default-y="0">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>2520</duration>
        <type>16th</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <beam number="2">end</beam>
        <notations>
          <slur number="4" type="stop" />
        </notations>
      </note>
      <note default-x="235.76" default-y="-5">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="5" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="277.52" default-y="-10">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="5" type="stop" />
        </notations>
      </note>
    </measure>
    <!--========================= Measure 17 =========================-->
    <measure number="17" width="237.09">
      <note default-x="20.96" default-y="-15">
        <pitch>
          <step>E</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <accidental>sharp</accidental>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="6" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="50.73" default-y="-10">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="6" type="stop" />
        </notations>
      </note>
      <note default-x="80.5" default-y="-5">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur number="1" placement="above" type="start" />
          <slur number="2" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="128.12" default-y="-5">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="1" type="stop" />
        </notations>
      </note>
      <note default-x="157.89" default-y="0">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="2" type="stop" />
        </notations>
      </note>
      <note default-x="187.66" default-y="5">
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur number="3" placement="above" type="start" />
          <slur number="4" placement="above" type="start" />
        </notations>
      </note>
    </measure>
    <!--========================= Measure 18 =========================-->
    <measure number="18" width="301.15">
      <print new-system="yes">
        <system-layout>
          <system-margins>
            <left-margin>68.85</left-margin>
            <right-margin>0</right-margin>
          </system-margins>
          <system-distance>105.03</system-distance>
        </system-layout>
      </print>
      <note default-x="116.87" default-y="5">
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="3" type="stop" />
        </notations>
      </note>
      <note default-x="143.7" default-y="10">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="4" type="stop" />
        </notations>
      </note>
      <note default-x="170.54" default-y="15">
        <pitch>
          <step>D</step>
          <octave>4</octave>
        </pitch>
        <duration>20160</duration>
        <type>half</type>
        <stem>down</stem>
        <notations>
          <slur number="5" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="256.41" default-y="10">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur number="5" type="stop" />
        </notations>
      </note>
    </measure>
    <!--========================= Measure 19 =========================-->
    <measure number="19" width="255.92">
      <note default-x="13" default-y="5">
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="6" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="44.62" default-y="0">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
        <notations>
          <slur number="6" type="stop" />
        </notations>
      </note>
      <note default-x="76.24" default-y="-5">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
        <notations>
          <slur number="1" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="107.87" default-y="-10">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="1" type="stop" />
        </notations>
      </note>
      <note default-x="139.49" default-y="-5">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="2" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="171.11" default-y="0">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>2520</duration>
        <type>16th</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
        <beam number="2">begin</beam>
      </note>
      <note default-x="190.87" default-y="5">
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>2520</duration>
        <type>16th</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <beam number="2">end</beam>
        <notations>
          <slur number="2" type="stop" />
        </notations>
      </note>
      <note default-x="210.64" default-y="0">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
    </measure>
    <!--========================= Measure 20 =========================-->
    <measure number="20" width="155.86">
      <note default-x="13.96" default-y="-10">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>40320</duration>
        <type>whole</type>
      </note>
    </measure>
    <!--========================= Measure 21 =========================-->
    <measure number="21" width="246.92">
      <note default-x="24.46" default-y="0">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>20160</duration>
        <type>half</type>
        <stem>down</stem>
        <notations>
          <slur number="3" placement="above" type="start" />
          <slur number="4" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="122.53" default-y="0">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="3" type="stop" />
        </notations>
      </note>
      <note default-x="153.18" default-y="10">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
      </note>
      <note default-x="183.82" default-y="5">
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
      </note>
      <note default-x="214.47" default-y="0">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="4" type="stop" />
        </notations>
      </note>
    </measure>
    <!--========================= Measure 22 =========================-->
    <measure number="22" width="304.39">
      <print new-page="yes">
        <system-layout>
          <system-margins>
            <left-margin>68.85</left-margin>
            <right-margin>0</right-margin>
          </system-margins>
          <top-system-distance>70</top-system-distance>
        </system-layout>
      </print>
      <note default-x="101.11" default-y="25">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>30240</duration>
        <type>half</type>
        <dot />
        <stem>down</stem>
      </note>
      <note default-x="239.5" default-y="20">
        <pitch>
          <step>E</step>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="5" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="273.76" default-y="15">
        <pitch>
          <step>D</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <accidental>sharp</accidental>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="5" type="stop" />
        </notations>
      </note>
    </measure>
    <!--========================= Measure 23 =========================-->
    <measure number="23" width="275.43">
      <note default-x="16.5" default-y="10">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>2520</duration>
        <type>16th</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <beam number="2">begin</beam>
        <notations>
          <slur number="6" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="38.12" default-y="5">
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>2520</duration>
        <type>16th</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
        <beam number="2">end</beam>
      </note>
      <note default-x="59.73" default-y="20">
        <pitch>
          <step>E</step>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="6" type="stop" />
        </notations>
      </note>
      <note default-x="94.32" default-y="-15">
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="141.87" default-y="-10">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>15120</duration>
        <type>quarter</type>
        <dot />
        <stem>down</stem>
        <notations>
          <slur number="1" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="224.01" default-y="-5">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>2520</duration>
        <type>16th</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <beam number="2">begin</beam>
      </note>
      <note default-x="245.63" default-y="0">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>2520</duration>
        <type>16th</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <beam number="2">end</beam>
        <notations>
          <slur number="1" type="stop" />
        </notations>
      </note>
    </measure>
    <!--========================= Measure 24 =========================-->
    <measure number="24" width="187.04">
      <note default-x="16.5" default-y="-5">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>15120</duration>
        <type>quarter</type>
        <dot />
        <stem>down</stem>
        <notations>
          <slur number="2" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="81.02" default-y="-10">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
      </note>
      <note default-x="105.83" default-y="-15">
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>20160</duration>
        <type>half</type>
        <stem>down</stem>
        <notations>
          <slur number="2" type="stop" />
        </notations>
      </note>
    </measure>
    <!--========================= Measure 25 =========================-->
    <measure number="25" width="192.99">
      <note default-x="16.5" default-y="0">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>30240</duration>
        <type>half</type>
        <dot />
        <stem>down</stem>
      </note>
      <note default-x="137.9" default-y="10">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="3" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="163.19" default-y="5">
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="3" type="stop" />
        </notations>
      </note>
    </measure>
    <!--========================= Measure 26 =========================-->
    <measure number="26" width="325.73">
      <print new-system="yes">
        <system-layout>
          <system-margins>
            <left-margin>68.85</left-margin>
            <right-margin>0</right-margin>
          </system-margins>
          <system-distance>228.28</system-distance>
        </system-layout>
      </print>
      <note default-x="116.87" default-y="5">
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>30240</duration>
        <type>half</type>
        <dot />
        <stem>down</stem>
      </note>
      <note default-x="263.03" default-y="15">
        <pitch>
          <step>D</step>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="4" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="293.48" default-y="10">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="4" type="stop" />
        </notations>
      </note>
    </measure>
    <!--========================= Measure 27 =========================-->
    <measure number="27" width="233.32">
      <note default-x="24.46" default-y="10">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>30240</duration>
        <type>half</type>
        <dot />
        <stem>down</stem>
      </note>
      <note default-x="170.62" default-y="20">
        <pitch>
          <step>E</step>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="5" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="201.07" default-y="15">
        <pitch>
          <step>D</step>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="5" type="stop" />
        </notations>
      </note>
    </measure>
    <!--========================= Measure 28 =========================-->
    <measure number="28" width="183.96">
      <note default-x="16.5" default-y="15">
        <pitch>
          <step>D</step>
          <octave>4</octave>
        </pitch>
        <duration>40320</duration>
        <type>whole</type>
      </note>
    </measure>
    <!--========================= Measure 29 =========================-->
    <measure number="29" width="216.83">
      <note default-x="13" default-y="-15">
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>20160</duration>
        <type>half</type>
        <stem>down</stem>
        <notations>
          <slur number="6" placement="above" type="start" />
          <slur number="1" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="102.79" default-y="-15">
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="6" type="stop" />
        </notations>
      </note>
      <note default-x="130.85" default-y="-5">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
      </note>
      <note default-x="158.91" default-y="5">
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
      </note>
      <note default-x="186.97" default-y="15">
        <pitch>
          <step>D</step>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="1" type="stop" />
        </notations>
      </note>
    </measure>
    <!--========================= Measure 30 =========================-->
    <measure number="30" width="383.74">
      <print new-system="yes">
        <system-layout>
          <system-margins>
            <left-margin>68.85</left-margin>
            <right-margin>0</right-margin>
          </system-margins>
          <system-distance>228.28</system-distance>
        </system-layout>
      </print>
      <note default-x="101.11" default-y="15">
        <pitch>
          <step>D</step>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="2" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="140.77" default-y="5">
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="2" type="stop" />
        </notations>
      </note>
      <note default-x="180.43" default-y="10">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>20160</duration>
        <type>half</type>
        <stem>down</stem>
        <notations>
          <slur number="3" placement="above" type="start" />
          <slur number="4" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="289.49" default-y="10">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="3" type="stop" />
        </notations>
      </note>
      <note default-x="329.15" default-y="15">
        <pitch>
          <step>D</step>
          <octave>4</octave>
        </pitch>
        <duration>2520</duration>
        <type>16th</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
        <beam number="2">begin</beam>
      </note>
      <note default-x="353.94" default-y="20">
        <pitch>
          <step>E</step>
          <octave>4</octave>
        </pitch>
        <duration>2520</duration>
        <type>16th</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <beam number="2">end</beam>
        <notations>
          <slur number="4" type="stop" />
        </notations>
      </note>
    </measure>
    <!--========================= Measure 31 =========================-->
    <measure number="31" width="240.83">
      <note default-x="13" default-y="0">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>20160</duration>
        <type>half</type>
        <stem>down</stem>
        <notations>
          <slur number="5" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="113.46" default-y="0">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="5" type="stop" />
        </notations>
      </note>
      <note default-x="144.85" default-y="10">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
        <notations>
          <slur number="6" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="176.24" default-y="20">
        <pitch>
          <step>E</step>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
      </note>
      <note default-x="207.64" default-y="30">
        <pitch>
          <step>G</step>
          <alter>0</alter>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <accidental>natural</accidental>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="6" type="stop" />
        </notations>
      </note>
    </measure>
    <!--========================= Measure 32 =========================-->
    <measure number="32" width="159.62">
      <note default-x="16.5" default-y="25">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>30240</duration>
        <type>half</type>
        <dot />
        <stem>down</stem>
      </note>
      <note default-x="122.49" default-y="0">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
    </measure>
    <!--========================= Measure 33 =========================-->
    <measure number="33" width="175.66">
      <note default-x="13" default-y="-5">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="1" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="36.66" default-y="5">
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="1" type="stop" />
        </notations>
      </note>
      <note default-x="60.31" default-y="15">
        <pitch>
          <step>D</step>
          <octave>4</octave>
        </pitch>
        <duration>20160</duration>
        <type>half</type>
        <stem>down</stem>
      </note>
      <note default-x="136.01" default-y="-10">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
    </measure>
    <!--========================= Measure 34 =========================-->
    <measure number="34" width="461.26">
      <print new-system="yes">
        <system-layout>
          <system-margins>
            <left-margin>68.85</left-margin>
            <right-margin>0</right-margin>
          </system-margins>
          <system-distance>228.28</system-distance>
        </system-layout>
      </print>
      <note default-x="101.11" default-y="-15">
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="165.73" default-y="5">
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="2" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="212.72" default-y="10">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>2520</duration>
        <type>16th</type>
        <stem>down</stem>
        <beam number="1">continue</beam>
        <beam number="2">begin</beam>
      </note>
      <note default-x="242.1" default-y="15">
        <pitch>
          <step>D</step>
          <octave>4</octave>
        </pitch>
        <duration>2520</duration>
        <type>16th</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <beam number="2">end</beam>
        <notations>
          <slur number="3" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="271.47" default-y="15">
        <pitch>
          <step>D</step>
          <octave>4</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <notations>
          <slur number="3" type="stop" />
        </notations>
      </note>
      <note default-x="318.47" default-y="10">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>4</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur number="2" type="stop" />
        </notations>
      </note>
      <note default-x="412.46" default-y="5">
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
      </note>
    </measure>
    <!--========================= Measure 35 =========================-->
    <measure number="35" width="331.5">
      <note default-x="13" default-y="0">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>2520</duration>
        <type>16th</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <beam number="2">begin</beam>
        <notations>
          <slur number="4" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="38.96" default-y="-5">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>2520</duration>
        <type>16th</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <beam number="2">end</beam>
      </note>
      <note default-x="64.92" default-y="-10">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="147.99" default-y="-5">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <notations>
          <slur number="4" type="stop" />
        </notations>
      </note>
      <note default-x="189.52" default-y="0">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="246.63" default-y="-5">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur number="5" placement="above" type="start" />
        </notations>
      </note>
      <note default-x="288.17" default-y="0">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>5040</duration>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur number="5" type="stop" />
        </notations>
      </note>
    </measure>
    <!--========================= Measure 36 =========================-->
    <measure number="36" width="167.08">
      <note default-x="13.96" default-y="0">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>40320</duration>
        <type>whole</type>
      </note>
      <barline location="right">
        <bar-style>light-heavy</bar-style>
      </barline>
    </measure>
  </part>
  <!--=========================== Part 2 ===========================-->
  <part id="P2">
    <!--========================= Measure 1 ==========================-->
    <measure number="1" width="264">
      <print>
        <staff-layout number="1">
          <staff-distance>42.01</staff-distance>
        </staff-layout>
      </print>
      <attributes>
        <divisions>10080</divisions>
        <key>
          <fifths>3</fifths>
        </key>
        <time>
          <beats>4</beats>
          <beat-type>4</beat-type>
        </time>
        <clef>
          <sign>F</sign>
          <line>4</line>
        </clef>
        <staff-details print-object="yes" />
      </attributes>
      <note default-x="124.2" default-y="-117.01">
        <pitch>
          <step>A</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="158.7" default-y="-82.01">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="193.2" default-y="-87.01">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="227.7" default-y="-122.01">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
    </measure>
    <!--========================= Measure 2 ==========================-->
    <measure number="2" width="157.27">
      <note default-x="17.46" default-y="-127.01">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="51.96" default-y="-92.01">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="86.46" default-y="-97.01">
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="120.97" default-y="-132.01">
        <pitch>
          <step>E</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
    </measure>
    <!--========================= Measure 3 ==========================-->
    <measure number="3" width="264.18">
      <note default-x="16.5" default-y="-137.01">
        <pitch>
          <step>D</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="68.26" default-y="-102.01">
        <pitch>
          <step>D</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="132.97" default-y="-102.01">
        <pitch>
          <step>D</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <accidental>sharp</accidental>
        <stem>down</stem>
      </note>
      <note default-x="197.67" default-y="-137.01">
        <pitch>
          <step>D</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <accidental>sharp</accidental>
        <stem>up</stem>
      </note>
    </measure>
    <!--========================= Measure 4 ==========================-->
    <measure number="4" width="201.42">
      <note default-x="16.5" default-y="-132.01">
        <pitch>
          <step>E</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="59.59" default-y="-97.01">
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="102.67" default-y="-102.01">
        <pitch>
          <step>D</step>
          <alter>0</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <accidental>natural</accidental>
        <stem>down</stem>
      </note>
      <note default-x="156.53" default-y="-137.01">
        <pitch>
          <step>D</step>
          <alter>0</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <accidental>natural</accidental>
        <stem>up</stem>
      </note>
    </measure>
    <!--========================= Measure 5 ==========================-->
    <measure number="5" width="307.15">
      <print new-system="yes">
        <staff-layout number="1">
          <staff-distance>42.01</staff-distance>
        </staff-layout>
      </print>
      <attributes>
        <staff-details print-object="yes" />
      </attributes>
      <note default-x="104.61" default-y="-142.01">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="154.79" default-y="-107.01">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="204.98" default-y="-112.01">
        <pitch>
          <step>B</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="255.16" default-y="-77.01">
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
    </measure>
    <!--========================= Measure 6 ==========================-->
    <measure number="6" width="393.47">
      <note default-x="20.96" default-y="-82.01">
        <pitch>
          <step>A</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <accidental>sharp</accidental>
        <stem>down</stem>
      </note>
      <note default-x="113.64" default-y="-117.01">
        <pitch>
          <step>A</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <accidental>sharp</accidental>
        <stem>up</stem>
      </note>
      <note default-x="206.32" default-y="-127.01">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="298.99" default-y="-92.01">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
    </measure>
    <!--========================= Measure 7 ==========================-->
    <measure number="7" width="259.23">
      <note default-x="17.46" default-y="-112.01">
        <pitch>
          <step>B</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="77.45" default-y="-77.01">
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="137.44" default-y="-82.01">
        <pitch>
          <step>A</step>
          <alter>0</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <accidental>natural</accidental>
        <stem>down</stem>
      </note>
      <note default-x="197.44" default-y="-117.01">
        <pitch>
          <step>A</step>
          <alter>0</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <accidental>natural</accidental>
        <stem>up</stem>
      </note>
    </measure>
    <!--========================= Measure 8 ==========================-->
    <measure number="8" width="403.01">
      <print new-system="yes">
        <staff-layout number="1">
          <staff-distance>42.01</staff-distance>
        </staff-layout>
      </print>
      <attributes>
        <staff-details print-object="yes" />
      </attributes>
      <note default-x="101.11" default-y="-122.01">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="176.13" default-y="-122.01">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="251.16" default-y="-132.01">
        <pitch>
          <step>E</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="326.19" default-y="-97.01">
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
    </measure>
    <!--========================= Measure 9 ==========================-->
    <measure number="9" width="235.97">
      <note default-x="16.5" default-y="-117.01">
        <pitch>
          <step>A</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="67.72" default-y="-82.01">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="118.93" default-y="-87.01">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="170.15" default-y="-122.01">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
    </measure>
    <!--========================= Measure 10 =========================-->
    <measure number="10" width="320.86">
      <note default-x="13" default-y="-127.01">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="68.19" default-y="-92.01">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="158.5" default-y="-102.01">
        <pitch>
          <step>D</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <accidental>sharp</accidental>
        <stem>down</stem>
      </note>
      <note default-x="238.78" default-y="-112.01">
        <pitch>
          <step>B</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
    </measure>
    <!--========================= Measure 11 =========================-->
    <measure number="11" width="372.26">
      <print new-system="yes">
        <staff-layout number="1">
          <staff-distance>42.01</staff-distance>
        </staff-layout>
      </print>
      <attributes>
        <staff-details print-object="yes" />
      </attributes>
      <note default-x="101.11" default-y="-97.01">
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="171.76" default-y="-117.01">
        <pitch>
          <step>A</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="251.24" default-y="-112.01">
        <pitch>
          <step>B</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="299.81" default-y="-112.01">
        <pitch>
          <step>B</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
    </measure>
    <!--========================= Measure 12 =========================-->
    <measure number="12" width="114.24">
      <note default-x="16.5" default-y="-132.01">
        <pitch>
          <step>E</step>
          <octave>2</octave>
        </pitch>
        <duration>40320</duration>
        <type>whole</type>
      </note>
    </measure>
    <!--========================= Measure 13 =========================-->
    <measure number="13" width="287.66">
      <note default-x="16.5" default-y="-132.01">
        <pitch>
          <step>E</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="67.59" default-y="-97.01">
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="118.67" default-y="-102.01">
        <pitch>
          <step>D</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="202.26" default-y="-137.01">
        <pitch>
          <step>D</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
    </measure>
    <!--========================= Measure 14 =========================-->
    <measure number="14" width="185.68">
      <note default-x="16.5" default-y="-142.01">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="58.34" default-y="-107.01">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="100.19" default-y="-112.01">
        <pitch>
          <step>B</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="142.03" default-y="-77.01">
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
    </measure>
    <!--========================= Measure 15 =========================-->
    <measure number="15" width="401.68">
      <print new-system="yes">
        <staff-layout number="1">
          <staff-distance>42.01</staff-distance>
        </staff-layout>
      </print>
      <attributes>
        <staff-details print-object="yes" />
      </attributes>
      <note default-x="113.37" default-y="-82.01">
        <pitch>
          <step>A</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <accidental>sharp</accidental>
        <stem>down</stem>
      </note>
      <note default-x="177.03" default-y="-117.01">
        <pitch>
          <step>A</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <accidental>sharp</accidental>
        <stem>up</stem>
      </note>
      <note default-x="240.7" default-y="-107.01">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="320.29" default-y="-127.01">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
    </measure>
    <!--========================= Measure 16 =========================-->
    <measure number="16" width="321.08">
      <note default-x="16.5" default-y="-112.01">
        <pitch>
          <step>B</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="73.92" default-y="-77.01">
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="131.35" default-y="-82.01">
        <pitch>
          <step>A</step>
          <alter>0</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <accidental>natural</accidental>
        <stem>down</stem>
      </note>
      <note default-x="235.76" default-y="-117.01">
        <pitch>
          <step>A</step>
          <alter>0</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <accidental>natural</accidental>
        <stem>up</stem>
      </note>
    </measure>
    <!--========================= Measure 17 =========================-->
    <measure number="17" width="237.09">
      <note default-x="20.96" default-y="-122.01">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="80.5" default-y="-87.01">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="128.12" default-y="-92.01">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="187.66" default-y="-127.01">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
    </measure>
    <!--========================= Measure 18 =========================-->
    <measure number="18" width="301.15">
      <print new-system="yes">
        <staff-layout number="1">
          <staff-distance>42.01</staff-distance>
        </staff-layout>
      </print>
      <attributes>
        <staff-details print-object="yes" />
      </attributes>
      <note default-x="116.87" default-y="-132.01">
        <pitch>
          <step>E</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <accidental>sharp</accidental>
        <stem>up</stem>
      </note>
      <note default-x="170.54" default-y="-127.01">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="213.47" default-y="-122.01">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="256.41" default-y="-132.01">
        <pitch>
          <step>E</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
    </measure>
    <!--========================= Measure 19 =========================-->
    <measure number="19" width="255.92">
      <note default-x="13" default-y="-127.01">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="76.24" default-y="-102.01">
        <pitch>
          <step>D</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="139.49" default-y="-112.01">
        <pitch>
          <step>B</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="210.64" default-y="-107.01">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
    </measure>
    <!--========================= Measure 20 =========================-->
    <measure number="20" width="155.86">
      <note default-x="14.92" default-y="-127.01">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="49.71" default-y="-92.01">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="84.49" default-y="-97.01">
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="119.28" default-y="-132.01">
        <pitch>
          <step>E</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
    </measure>
    <!--========================= Measure 21 =========================-->
    <measure number="21" width="246.92">
      <note default-x="24.46" default-y="-137.01">
        <pitch>
          <step>D</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <accidental>sharp</accidental>
        <stem>up</stem>
      </note>
      <note default-x="73.49" default-y="-102.01">
        <pitch>
          <step>D</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <accidental>sharp</accidental>
        <stem>down</stem>
      </note>
      <note default-x="122.53" default-y="-107.01">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="183.82" default-y="-107.01">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
    </measure>
    <!--========================= Measure 22 =========================-->
    <measure number="22" width="304.39">
      <print new-page="yes">
        <staff-layout number="1">
          <staff-distance>91.31</staff-distance>
        </staff-layout>
      </print>
      <attributes>
        <staff-details print-object="yes" />
      </attributes>
      <note default-x="101.11" default-y="-161.31">
        <pitch>
          <step>B</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="147.24" default-y="-126.31">
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="193.37" default-y="-131.31">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="239.5" default-y="-166.31">
        <pitch>
          <step>A</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
    </measure>
    <!--========================= Measure 23 =========================-->
    <measure number="23" width="275.43">
      <note default-x="16.5" default-y="-171.31">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="94.32" default-y="-171.31">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="141.87" default-y="-166.31">
        <pitch>
          <step>A</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="189.43" default-y="-161.31">
        <pitch>
          <step>B</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
    </measure>
    <!--========================= Measure 24 =========================-->
    <measure number="24" width="187.04">
      <note default-x="16.5" default-y="-181.31">
        <pitch>
          <step>E</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="56.2" default-y="-146.31">
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="105.83" default-y="-151.31">
        <pitch>
          <step>D</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="145.54" default-y="-186.31">
        <pitch>
          <step>D</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
    </measure>
    <!--========================= Measure 25 =========================-->
    <measure number="25" width="192.99">
      <note default-x="16.5" default-y="-191.31">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="56.97" default-y="-156.31">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="97.43" default-y="-151.31">
        <pitch>
          <step>D</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="137.9" default-y="-186.31">
        <pitch>
          <step>D</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
    </measure>
    <!--========================= Measure 26 =========================-->
    <measure number="26" width="325.73">
      <print new-system="yes">
        <staff-layout number="1">
          <staff-distance>91.31</staff-distance>
        </staff-layout>
      </print>
      <attributes>
        <staff-details print-object="yes" />
      </attributes>
      <note default-x="116.87" default-y="-186.31">
        <pitch>
          <step>D</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <accidental>sharp</accidental>
        <stem>up</stem>
      </note>
      <note default-x="165.59" default-y="-151.31">
        <pitch>
          <step>D</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <accidental>sharp</accidental>
        <stem>down</stem>
      </note>
      <note default-x="214.31" default-y="-146.31">
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="263.03" default-y="-181.31">
        <pitch>
          <step>E</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
    </measure>
    <!--========================= Measure 27 =========================-->
    <measure number="27" width="233.32">
      <note default-x="24.46" default-y="-181.31">
        <pitch>
          <step>E</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <accidental>sharp</accidental>
        <stem>up</stem>
      </note>
      <note default-x="73.18" default-y="-146.31">
        <pitch>
          <step>E</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <accidental>sharp</accidental>
        <stem>down</stem>
      </note>
      <note default-x="121.9" default-y="-141.31">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="170.62" default-y="-176.31">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
    </measure>
    <!--========================= Measure 28 =========================-->
    <measure number="28" width="183.96">
      <note default-x="17.46" default-y="-161.31">
        <pitch>
          <step>B</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="58.64" default-y="-126.31">
        <pitch>
          <step>B</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="99.81" default-y="-131.31">
        <pitch>
          <step>A</step>
          <alter>0</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <accidental>natural</accidental>
        <stem>down</stem>
      </note>
      <note default-x="140.99" default-y="-166.31">
        <pitch>
          <step>A</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
    </measure>
    <!--========================= Measure 29 =========================-->
    <measure number="29" width="216.83">
      <note default-x="13" default-y="-171.31">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="57.9" default-y="-136.31">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="102.79" default-y="-146.31">
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="158.91" default-y="-136.31">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
    </measure>
    <!--========================= Measure 30 =========================-->
    <measure number="30" width="383.74">
      <print new-system="yes">
        <staff-layout number="1">
          <staff-distance>91.31</staff-distance>
        </staff-layout>
      </print>
      <attributes>
        <staff-details print-object="yes" />
      </attributes>
      <note default-x="101.11" default-y="-131.31">
        <pitch>
          <step>A</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="180.43" default-y="-166.31">
        <pitch>
          <step>A</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="234.96" default-y="-171.31">
        <pitch>
          <step>G</step>
          <alter>0</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <accidental>natural</accidental>
        <stem>up</stem>
      </note>
      <note default-x="289.49" default-y="-136.31">
        <pitch>
          <step>G</step>
          <alter>0</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <accidental>natural</accidental>
        <stem>down</stem>
      </note>
    </measure>
    <!--========================= Measure 31 =========================-->
    <measure number="31" width="240.83">
      <note default-x="13" default-y="-141.31">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="63.23" default-y="-176.31">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="113.46" default-y="-181.31">
        <pitch>
          <step>E</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="176.24" default-y="-146.31">
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
    </measure>
    <!--========================= Measure 32 =========================-->
    <measure number="32" width="159.62">
      <note default-x="16.5" default-y="-151.31">
        <pitch>
          <step>D</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="51.83" default-y="-186.31">
        <pitch>
          <step>D</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="87.16" default-y="-191.31">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="122.49" default-y="-156.31">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
    </measure>
    <!--========================= Measure 33 =========================-->
    <measure number="33" width="175.66">
      <note default-x="13" default-y="-161.31">
        <pitch>
          <step>B</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="60.31" default-y="-161.31">
        <pitch>
          <step>B</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="98.16" default-y="-166.31">
        <pitch>
          <step>A</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="136.01" default-y="-166.31">
        <pitch>
          <step>A</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
    </measure>
    <!--========================= Measure 34 =========================-->
    <measure number="34" width="461.26">
      <print new-system="yes">
        <staff-layout number="1">
          <staff-distance>91.31</staff-distance>
        </staff-layout>
      </print>
      <attributes>
        <staff-details print-object="yes" />
      </attributes>
      <note default-x="101.11" default-y="-171.31">
        <pitch>
          <step>G</step>
          <alter>1</alter>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="165.73" default-y="-181.31">
        <pitch>
          <step>E</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="271.47" default-y="-166.31">
        <pitch>
          <step>A</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
      <note default-x="365.47" default-y="-151.31">
        <pitch>
          <step>D</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
    </measure>
    <!--========================= Measure 35 =========================-->
    <measure number="35" width="331.5">
      <note default-x="13" default-y="-146.31">
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="106.45" default-y="-151.31">
        <pitch>
          <step>D</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="189.52" default-y="-146.31">
        <pitch>
          <step>E</step>
          <octave>3</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>down</stem>
      </note>
      <note default-x="246.63" default-y="-181.31">
        <pitch>
          <step>E</step>
          <octave>2</octave>
        </pitch>
        <duration>10080</duration>
        <type>quarter</type>
        <stem>up</stem>
      </note>
    </measure>
    <!--========================= Measure 36 =========================-->
    <measure number="36" width="167.08">
      <note default-x="13.96" default-y="-166.31">
        <pitch>
          <step>A</step>
          <octave>2</octave>
        </pitch>
        <duration>40320</duration>
        <type>whole</type>
      </note>
      <barline location="right">
        <bar-style>light-heavy</bar-style>
      </barline>
    </measure>
  </part>
  </score-partwise>`,
    "twelve_duets.musicxml": `<?xml version="1.0" encoding="UTF-8"?>
  <score-partwise version="3.1">
    <work>
    <work-title>Twelve Duets k. 487 No. 2</work-title>
    </work>
  <identification>
    <creator type="composer">W.A. Mozart</creator>
    <encoding>
      <software>MuseScore 3.6.2</software>
      <encoding-date>2024-09-10</encoding-date>
      <supports element="accidental" type="yes"/>
      <supports element="beam" type="yes"/>
      <supports element="print" attribute="new-page" type="yes" value="yes"/>
      <supports element="print" attribute="new-system" type="yes" value="yes"/>
      <supports element="stem" type="yes"/>
      </encoding>
    </identification>
  <defaults>
    <scaling>
      <millimeters>6.99912</millimeters>
      <tenths>40</tenths>
      </scaling>
    <page-layout>
      <page-height>1596.77</page-height>
      <page-width>1233.87</page-width>
      <page-margins type="even">
        <left-margin>85.7251</left-margin>
        <right-margin>85.7251</right-margin>
        <top-margin>85.7251</top-margin>
        <bottom-margin>85.7251</bottom-margin>
        </page-margins>
      <page-margins type="odd">
        <left-margin>85.7251</left-margin>
        <right-margin>85.7251</right-margin>
        <top-margin>85.7251</top-margin>
        <bottom-margin>85.7251</bottom-margin>
        </page-margins>
      </page-layout>
    <word-font font-family="Edwin" font-size="10"/>
    <lyric-font font-family="Edwin" font-size="10"/>
    </defaults>
  <credit page="1">
    <credit-type>title</credit-type>
    <credit-words default-x="616.935" default-y="1511.05" justify="center" valign="top" font-size="22">Twelve Duets k. 487 No. 2</credit-words>
    </credit>
  <credit page="1">
    <credit-type>composer</credit-type>
    <credit-words default-x="1148.14" default-y="1411.05" justify="right" valign="bottom">W.A. Mozart</credit-words>
    </credit>
  <part-list>
    <part-group type="start" number="1">
      <group-symbol>bracket</group-symbol>
      </part-group>
    <part-group type="start" number="2">
      <group-symbol>square</group-symbol>
      </part-group>
    <score-part id="P1">
      <part-name>Violoncello 1</part-name>
      <part-abbreviation>Vc. 1</part-abbreviation>
      <score-instrument id="P1-I1">
        <instrument-name>Violoncello</instrument-name>
        </score-instrument>
      <midi-device id="P1-I1" port="1"></midi-device>
      <midi-instrument id="P1-I1">
        <midi-channel>1</midi-channel>
        <midi-program>43</midi-program>
        <volume>78.7402</volume>
        <pan>0</pan>
        </midi-instrument>
      </score-part>
    <score-part id="P2">
      <part-name>Violoncello 2</part-name>
      <part-abbreviation>Vc. 2</part-abbreviation>
      <score-instrument id="P2-I1">
        <instrument-name>Violoncello</instrument-name>
        </score-instrument>
      <midi-device id="P2-I1" port="1"></midi-device>
      <midi-instrument id="P2-I1">
        <midi-channel>4</midi-channel>
        <midi-program>43</midi-program>
        <volume>78.7402</volume>
        <pan>0</pan>
        </midi-instrument>
      </score-part>
    <part-group type="stop" number="2"/>
    <part-group type="stop" number="1"/>
    </part-list>
  <part id="P1">
    <measure number="1" width="195.79">
      <print>
        <system-layout>
          <system-margins>
            <left-margin>141.84</left-margin>
            <right-margin>0.00</right-margin>
            </system-margins>
          <top-system-distance>170.00</top-system-distance>
          </system-layout>
        </print>
      <attributes>
        <divisions>2</divisions>
        <key>
          <fifths>1</fifths>
          </key>
        <time>
          <beats>3</beats>
          <beat-type>4</beat-type>
          </time>
        <clef>
          <sign>F</sign>
          <line>4</line>
          </clef>
        </attributes>
      <direction placement="below">
        <direction-type>
          <dynamics default-x="3.25" default-y="-40.00" relative-y="-25.00">
            <f/>
            </dynamics>
          </direction-type>
        <sound dynamics="106.67"/>
        </direction>
      <direction placement="above">
        <direction-type>
          <words default-x="-37.68" default-y="11.80" relative-y="20.00" font-weight="bold" font-size="12">Allegro - Menuetto</words>
          </direction-type>
        <sound tempo="118"/>
        </direction>
      <note default-x="103.23" default-y="15.00">
        <pitch>
          <step>D</step>
          <octave>4</octave>
          </pitch>
        <duration>4</duration>
        <voice>1</voice>
        <type>half</type>
        <stem>down</stem>
        </note>
      <note default-x="159.08" default-y="5.00">
        <pitch>
          <step>B</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      </measure>
    <measure number="2" width="127.45">
      <note default-x="16.50" default-y="10.00">
        <pitch>
          <step>C</step>
          <octave>4</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="52.88" default-y="0.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="89.27" default-y="0.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      </measure>
    <measure number="3" width="186.64">
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      <note default-x="64.60" default-y="0.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur type="start" placement="above" number="1"/>
          </notations>
        </note>
      <note default-x="94.66" default-y="5.00">
        <pitch>
          <step>B</step>
          <octave>3</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      <note default-x="124.72" default-y="10.00">
        <pitch>
          <step>C</step>
          <octave>4</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="154.78" default-y="0.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      </measure>
    <measure number="4" width="177.54">
      <note default-x="13.00" default-y="5.00">
        <pitch>
          <step>B</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <tenuto/>
            </articulations>
          </notations>
        </note>
      <note default-x="59.50" default-y="-5.00">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="88.56" default-y="0.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="117.62" default-y="5.00">
        <pitch>
          <step>B</step>
          <octave>3</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="146.68" default-y="10.00">
        <pitch>
          <step>C</step>
          <octave>4</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      </measure>
    <measure number="5" width="199.44">
      <note default-x="16.50" default-y="15.00">
        <pitch>
          <step>D</step>
          <octave>4</octave>
          </pitch>
        <duration>4</duration>
        <voice>1</voice>
        <type>half</type>
        <stem>down</stem>
        </note>
      <note default-x="137.26" default-y="5.00">
        <pitch>
          <step>B</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      </measure>
    <measure number="6" width="187.37">
      <print new-system="yes">
        <system-layout>
          <system-margins>
            <left-margin>68.85</left-margin>
            <right-margin>0.00</right-margin>
            </system-margins>
          <system-distance>85.00</system-distance>
          </system-layout>
        </print>
      <note default-x="61.92" default-y="15.00">
        <grace slash="yes"/>
        <pitch>
          <step>D</step>
          <octave>4</octave>
          </pitch>
        <voice>1</voice>
        <type>eighth</type>
        <stem>up</stem>
        </note>
      <note default-x="81.11" default-y="10.00">
        <pitch>
          <step>C</step>
          <octave>4</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <accent/>
            </articulations>
          </notations>
        </note>
      <note default-x="115.93" default-y="0.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="150.75" default-y="0.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      </measure>
    <measure number="7" width="181.95">
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      <note default-x="63.26" default-y="0.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur type="start" placement="above" number="1"/>
          </notations>
        </note>
      <note default-x="92.48" default-y="5.00">
        <pitch>
          <step>B</step>
          <octave>3</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      <note default-x="121.71" default-y="10.00">
        <pitch>
          <step>C</step>
          <octave>4</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="150.93" default-y="0.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        </note>
      </measure>
    <measure number="8" width="119.26">
      <note default-x="13.00" default-y="-5.00">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <tenuto/>
            </articulations>
          </notations>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      </measure>
    <measure number="9" width="95.27">
      <direction placement="below">
        <direction-type>
          <dynamics default-x="3.25" default-y="-40.00" relative-y="-25.00">
            <p/>
            </dynamics>
          </direction-type>
        <sound dynamics="54.44"/>
        </direction>
      <note default-x="13.00" default-y="0.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>4</duration>
        <voice>1</voice>
        <type>half</type>
        <stem>down</stem>
        <notations>
          <slur type="start" placement="above" number="1"/>
          </notations>
        </note>
      <note default-x="62.52" default-y="5.00">
        <pitch>
          <step>B</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      </measure>
    <measure number="10" width="119.26">
      <note default-x="13.00" default-y="-5.00">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="start" placement="above" number="1"/>
          </notations>
        </note>
      <note default-x="47.82" default-y="-10.00">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        </note>
      <note default-x="82.64" default-y="-5.00">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      </measure>
    <measure number="11" width="122.76">
      <note default-x="16.50" default-y="10.00">
        <pitch>
          <step>C</step>
          <octave>4</octave>
          </pitch>
        <duration>4</duration>
        <voice>1</voice>
        <type>half</type>
        <stem>down</stem>
        <notations>
          <slur type="start" placement="above" number="1"/>
          </notations>
        </note>
      <note default-x="86.14" default-y="-5.00">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      </measure>
    <measure number="12" width="133.96">
      <note default-x="16.50" default-y="0.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="start" placement="above" number="1"/>
          </notations>
        </note>
      <note default-x="55.05" default-y="20.00">
        <pitch>
          <step>E</step>
          <octave>4</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        </note>
      <note default-x="93.61" default-y="15.00">
        <pitch>
          <step>D</step>
          <octave>4</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      </measure>
    <measure number="13" width="193.18">
      <print new-system="yes">
        <system-layout>
          <system-margins>
            <left-margin>68.85</left-margin>
            <right-margin>0.00</right-margin>
            </system-margins>
          <system-distance>85.00</system-distance>
          </system-layout>
        </print>
      <note default-x="96.87" default-y="10.00">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>4</octave>
          </pitch>
        <duration>6</duration>
        <voice>1</voice>
        <type>half</type>
        <dot/>
        <accidental>sharp</accidental>
        <stem>down</stem>
        <notations>
          <slur type="start" placement="above" number="1"/>
          </notations>
        </note>
      </measure>
    <measure number="14" width="112.81">
      <note default-x="16.50" default-y="15.00">
        <pitch>
          <step>D</step>
          <octave>4</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      <note default-x="48.00" default-y="0.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        </note>
      <note default-x="79.51" default-y="0.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        </note>
      </measure>
    <measure number="15" width="93.27">
      <note default-x="20.96" default-y="5.00">
        <pitch>
          <step>B</step>
          <alter>-1</alter>
          <octave>3</octave>
          </pitch>
        <duration>4</duration>
        <voice>1</voice>
        <type>half</type>
        <accidental>flat</accidental>
        <stem>down</stem>
        <notations>
          <slur type="start" placement="above" number="1"/>
          </notations>
        </note>
      <note default-x="63.48" default-y="-5.00">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      </measure>
    <measure number="16" width="181.36">
      <note default-x="13.00" default-y="-10.00">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        </note>
      <direction placement="below">
        <direction-type>
          <wedge type="crescendo" number="1" default-y="-60.00"/>
          </direction-type>
        </direction>
      <note default-x="60.59" default-y="-5.00">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur type="start" placement="above" number="1"/>
          </notations>
        </note>
      <note default-x="90.33" default-y="0.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      <note default-x="120.07" default-y="5.00">
        <pitch>
          <step>B</step>
          <octave>3</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <accidental>natural</accidental>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="149.82" default-y="10.00">
        <pitch>
          <step>C</step>
          <octave>4</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <direction placement="below">
        <direction-type>
          <wedge type="stop" number="1"/>
          </direction-type>
        </direction>
      </measure>
    <measure number="17" width="94.42">
      <note default-x="16.50" default-y="15.00">
        <pitch>
          <step>D</step>
          <octave>4</octave>
          </pitch>
        <duration>4</duration>
        <voice>1</voice>
        <type>half</type>
        <stem>down</stem>
        </note>
      <note default-x="63.34" default-y="5.00">
        <pitch>
          <step>B</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      </measure>
    <measure number="18" width="112.81">
      <note default-x="16.50" default-y="10.00">
        <pitch>
          <step>C</step>
          <octave>4</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="48.00" default-y="0.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="79.51" default-y="0.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      </measure>
    <measure number="19" width="172.00">
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      <note default-x="60.22" default-y="0.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur type="start" placement="above" number="1"/>
          </notations>
        </note>
      <note default-x="87.55" default-y="5.00">
        <pitch>
          <step>B</step>
          <octave>3</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      <note default-x="114.88" default-y="10.00">
        <pitch>
          <step>C</step>
          <octave>4</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="142.20" default-y="0.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      </measure>
    <measure number="20" width="241.11">
      <print new-system="yes">
        <system-layout>
          <system-margins>
            <left-margin>68.85</left-margin>
            <right-margin>0.00</right-margin>
            </system-margins>
          <system-distance>85.00</system-distance>
          </system-layout>
        </print>
      <note default-x="81.11" default-y="5.00">
        <pitch>
          <step>B</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <tenuto/>
            </articulations>
          </notations>
        </note>
      <note default-x="126.31" default-y="-5.00">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="154.56" default-y="0.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="182.81" default-y="5.00">
        <pitch>
          <step>B</step>
          <octave>3</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="211.06" default-y="10.00">
        <pitch>
          <step>C</step>
          <octave>4</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      </measure>
    <measure number="21" width="194.90">
      <note default-x="16.50" default-y="15.00">
        <pitch>
          <step>D</step>
          <octave>4</octave>
          </pitch>
        <duration>4</duration>
        <voice>1</voice>
        <type>half</type>
        <stem>down</stem>
        </note>
      <note default-x="134.23" default-y="5.00">
        <pitch>
          <step>B</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      </measure>
    <measure number="22" width="142.10">
      <note default-x="16.50" default-y="15.00">
        <grace slash="yes"/>
        <pitch>
          <step>D</step>
          <octave>4</octave>
          </pitch>
        <voice>1</voice>
        <type>eighth</type>
        <stem>up</stem>
        </note>
      <note default-x="35.69" default-y="10.00">
        <pitch>
          <step>C</step>
          <octave>4</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <accent/>
            </articulations>
          </notations>
        </note>
      <note default-x="70.56" default-y="0.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="105.43" default-y="0.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      </measure>
    <measure number="23" width="176.50">
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      <note default-x="61.70" default-y="0.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <slur type="start" placement="above" number="1"/>
          </notations>
        </note>
      <note default-x="89.95" default-y="5.00">
        <pitch>
          <step>B</step>
          <octave>3</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      <note default-x="118.20" default-y="10.00">
        <pitch>
          <step>C</step>
          <octave>4</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="146.45" default-y="0.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      </measure>
    <measure number="24" width="119.41">
      <note default-x="13.00" default-y="-5.00">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <tenuto/>
            </articulations>
          </notations>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      <direction placement="above">
        <direction-type>
          <words relative-y="20.00">Fine</words>
          </direction-type>
        <sound fine="yes"/>
        </direction>
      </measure>
    <measure number="25" width="85.82">
      <direction placement="below">
        <direction-type>
          <dynamics default-x="3.25" default-y="-40.00" relative-y="-25.00">
            <p/>
            </dynamics>
          </direction-type>
        <sound dynamics="54.44"/>
        </direction>
      <note default-x="13.00" default-y="5.00">
        <pitch>
          <step>B</step>
          <octave>3</octave>
          </pitch>
        <duration>6</duration>
        <voice>1</voice>
        <type>half</type>
        <dot/>
        <stem>down</stem>
        </note>
      </measure>
    <measure number="26" width="165.46">
      <print new-system="yes">
        <system-layout>
          <system-margins>
            <left-margin>68.85</left-margin>
            <right-margin>0.00</right-margin>
            </system-margins>
          <system-distance>85.00</system-distance>
          </system-layout>
        </print>
      <note default-x="81.11" default-y="10.00">
        <pitch>
          <step>C</step>
          <octave>4</octave>
          </pitch>
        <duration>4</duration>
        <voice>1</voice>
        <type>half</type>
        <stem>down</stem>
        <notations>
          <slur type="start" placement="above" number="1"/>
          </notations>
        </note>
      <note default-x="131.91" default-y="5.00">
        <pitch>
          <step>B</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      </measure>
    <measure number="27" width="123.71">
      <note default-x="20.96" default-y="0.00">
        <pitch>
          <step>A</step>
          <alter>1</alter>
          <octave>3</octave>
          </pitch>
        <duration>6</duration>
        <voice>1</voice>
        <type>half</type>
        <dot/>
        <accidental>sharp</accidental>
        <stem>down</stem>
        <notations>
          <slur type="start" placement="above" number="1"/>
          </notations>
        </note>
      </measure>
    <measure number="28" width="123.71">
      <note default-x="20.96" default-y="5.00">
        <pitch>
          <step>B</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      </measure>
    <measure number="29" width="91.75">
      <note default-x="13.00" default-y="5.00">
        <pitch>
          <step>B</step>
          <octave>3</octave>
          </pitch>
        <duration>4</duration>
        <voice>1</voice>
        <type>half</type>
        <stem>down</stem>
        </note>
      <note default-x="60.35" default-y="5.00">
        <pitch>
          <step>B</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="start" placement="above" number="1"/>
          <slur type="start" placement="above" number="2"/>
          </notations>
        </note>
      </measure>
    <measure number="30" width="115.75">
      <note default-x="13.00" default-y="5.00">
        <pitch>
          <step>B</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      <note default-x="46.65" default-y="0.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="stop" number="2"/>
          </notations>
        </note>
      <note default-x="80.30" default-y="20.00">
        <pitch>
          <step>E</step>
          <octave>4</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="start" placement="above" number="1"/>
          <slur type="start" placement="above" number="2"/>
          </notations>
        </note>
      </measure>
    <measure number="31" width="131.98">
      <note default-x="18.04" default-y="20.00">
        <pitch>
          <step>E</step>
          <octave>4</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      <note default-x="55.42" default-y="15.00">
        <pitch>
          <step>D</step>
          <octave>4</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="stop" number="2"/>
          </notations>
        </note>
      <note default-x="92.80" default-y="-10.00">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      </measure>
    <measure number="32" width="115.75">
      <note default-x="13.00" default-y="-5.00">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      </measure>
    <measure number="33" width="91.75">
      <direction placement="below">
        <direction-type>
          <dynamics default-x="3.25" default-y="-40.00" relative-y="-25.00">
            <mp/>
            </dynamics>
          </direction-type>
        <sound dynamics="71.11"/>
        </direction>
      <note default-x="13.00" default-y="5.00">
        <pitch>
          <step>B</step>
          <octave>3</octave>
          </pitch>
        <duration>4</duration>
        <voice>1</voice>
        <type>half</type>
        <stem>down</stem>
        <notations>
          <slur type="start" placement="above" number="1"/>
          </notations>
        </note>
      <note default-x="60.35" default-y="0.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      </measure>
    <measure number="34" width="195.25">
      <print new-system="yes">
        <system-layout>
          <system-margins>
            <left-margin>68.85</left-margin>
            <right-margin>0.00</right-margin>
            </system-margins>
          <system-distance>85.00</system-distance>
          </system-layout>
        </print>
      <direction placement="below">
        <direction-type>
          <wedge type="crescendo" number="1" default-y="-60.00"/>
          </direction-type>
        </direction>
      <note default-x="81.11" default-y="0.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>4</duration>
        <voice>1</voice>
        <type>half</type>
        <stem>down</stem>
        <notations>
          <slur type="start" placement="above" number="1"/>
          </notations>
        </note>
      <note default-x="150.24" default-y="-10.00">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      <direction placement="below">
        <direction-type>
          <wedge type="stop" number="1"/>
          </direction-type>
        </direction>
      </measure>
    <measure number="35" width="113.11">
      <direction placement="below">
        <direction-type>
          <dynamics default-x="3.25" default-y="-40.00" relative-y="-25.00">
            <mf/>
            </dynamics>
          </direction-type>
        <sound dynamics="88.89"/>
        </direction>
      <direction placement="below">
        <direction-type>
          <wedge type="diminuendo" number="1" default-y="-60.00"/>
          </direction-type>
        </direction>
      <note default-x="16.50" default-y="10.00">
        <pitch>
          <step>C</step>
          <octave>4</octave>
          </pitch>
        <duration>4</duration>
        <voice>1</voice>
        <type>half</type>
        <stem>down</stem>
        <notations>
          <slur type="start" placement="above" number="1"/>
          </notations>
        </note>
      <note default-x="74.84" default-y="5.00">
        <pitch>
          <step>B</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      </measure>
    <measure number="36" width="104.01">
      <note default-x="13.00" default-y="0.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>4</duration>
        <voice>1</voice>
        <type>half</type>
        <stem>down</stem>
        <notations>
          <slur type="start" placement="above" number="1"/>
          </notations>
        </note>
      <direction placement="below">
        <direction-type>
          <wedge type="stop" number="1"/>
          </direction-type>
        </direction>
      <note default-x="67.90" default-y="-5.00">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      </measure>
    <measure number="37" width="128.00">
      <direction placement="below">
        <direction-type>
          <dynamics default-x="3.25" default-y="-40.00" relative-y="-25.00">
            <p/>
            </dynamics>
          </direction-type>
        <sound dynamics="54.44"/>
        </direction>
      <direction placement="below">
        <direction-type>
          <wedge type="crescendo" number="1" default-y="-60.00"/>
          </direction-type>
        </direction>
      <note default-x="13.00" default-y="5.00">
        <pitch>
          <step>B</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="50.73" default-y="5.00">
        <pitch>
          <step>B</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="88.47" default-y="5.00">
        <pitch>
          <step>B</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <direction placement="below">
        <direction-type>
          <wedge type="stop" number="1"/>
          </direction-type>
        </direction>
      </measure>
    <measure number="38" width="131.50">
      <direction placement="below">
        <direction-type>
          <wedge type="diminuendo" number="1" default-y="-60.00"/>
          </direction-type>
        </direction>
      <note default-x="16.50" default-y="10.00">
        <pitch>
          <step>C</step>
          <octave>4</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="start" placement="above" number="1"/>
          </notations>
        </note>
      <note default-x="54.23" default-y="0.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        </note>
      <note default-x="91.97" default-y="-10.00">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      <direction placement="below">
        <direction-type>
          <wedge type="stop" number="1"/>
          </direction-type>
        </direction>
      </measure>
    <measure number="39" width="151.14">
      <note default-x="13.00" default-y="-20.00">
        <pitch>
          <step>D</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="start" placement="above" number="1"/>
          </notations>
        </note>
      <note default-x="58.45" default-y="-10.00">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      <note default-x="103.89" default-y="-20.00">
        <pitch>
          <step>D</step>
          <alter>1</alter>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <accidental>sharp</accidental>
        <stem>down</stem>
        </note>
      </measure>
    <measure number="40" width="136.85">
      <note default-x="13.00" default-y="-15.00">
        <pitch>
          <step>E</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      <direction placement="above">
        <direction-type>
          <words relative-y="20.00">D.C. al Fine</words>
          </direction-type>
        <sound dacapo="yes"/>
        </direction>
      <barline location="right">
        <bar-style>light-heavy</bar-style>
        </barline>
      </measure>
    </part>
  <part id="P2">
    <measure number="1" width="195.79">
      <print>
        <staff-layout number="1">
          <staff-distance>48.76</staff-distance>
          </staff-layout>
        </print>
      <attributes>
        <divisions>2</divisions>
        <key>
          <fifths>1</fifths>
          </key>
        <time>
          <beats>3</beats>
          <beat-type>4</beat-type>
          </time>
        <clef>
          <sign>F</sign>
          <line>4</line>
          </clef>
        </attributes>
      <direction placement="below">
        <direction-type>
          <dynamics default-x="3.25" default-y="-40.00" relative-y="-25.00">
            <f/>
            </dynamics>
          </direction-type>
        <sound dynamics="106.67"/>
        </direction>
      <note default-x="103.23" default-y="-83.76">
        <pitch>
          <step>B</step>
          <octave>3</octave>
          </pitch>
        <duration>4</duration>
        <voice>1</voice>
        <type>half</type>
        <stem>down</stem>
        </note>
      <note default-x="159.08" default-y="-93.76">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      </measure>
    <measure number="2" width="127.45">
      <note default-x="16.50" default-y="-88.76">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="52.88" default-y="-108.76">
        <pitch>
          <step>D</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="89.27" default-y="-108.76">
        <pitch>
          <step>D</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      </measure>
    <measure number="3" width="186.64">
      <note default-x="16.50" default-y="-143.76">
        <pitch>
          <step>D</step>
          <octave>2</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>up</stem>
        <notations>
          <articulations>
            <tenuto/>
            </articulations>
          </notations>
        </note>
      <note default-x="64.60" default-y="-108.76">
        <pitch>
          <step>D</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="124.72" default-y="-108.76">
        <pitch>
          <step>D</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      </measure>
    <measure number="4" width="177.54">
      <note default-x="13.00" default-y="-93.76">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <tenuto/>
            </articulations>
          </notations>
        </note>
      <note default-x="59.50" default-y="-128.76">
        <pitch>
          <step>G</step>
          <octave>2</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>up</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="117.62" default-y="-128.76">
        <pitch>
          <step>G</step>
          <octave>2</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>up</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      </measure>
    <measure number="5" width="199.44">
      <note default-x="16.50" default-y="-128.76">
        <pitch>
          <step>G</step>
          <octave>2</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>up</stem>
        <beam number="1">begin</beam>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="46.69" default-y="-128.76">
        <pitch>
          <step>G</step>
          <octave>2</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>up</stem>
        <beam number="1">end</beam>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="76.88" default-y="-118.76">
        <pitch>
          <step>B</step>
          <octave>2</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>up</stem>
        <beam number="1">begin</beam>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="107.07" default-y="-108.76">
        <pitch>
          <step>D</step>
          <octave>3</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>up</stem>
        <beam number="1">end</beam>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="137.26" default-y="-88.76">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="167.45" default-y="-108.76">
        <pitch>
          <step>D</step>
          <octave>3</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      </measure>
    <measure number="6" width="187.37">
      <print new-system="yes">
        <staff-layout number="1">
          <staff-distance>37.40</staff-distance>
          </staff-layout>
        </print>
      <note default-x="81.11" default-y="-77.40">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <accent/>
            </articulations>
          </notations>
        </note>
      <note default-x="115.93" default-y="-97.40">
        <pitch>
          <step>D</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="150.75" default-y="-97.40">
        <pitch>
          <step>D</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      </measure>
    <measure number="7" width="181.95">
      <note default-x="16.50" default-y="-132.40">
        <pitch>
          <step>D</step>
          <octave>2</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>up</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="63.26" default-y="-97.40">
        <pitch>
          <step>D</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="121.71" default-y="-97.40">
        <pitch>
          <step>D</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      </measure>
    <measure number="8" width="119.26">
      <note default-x="13.00" default-y="-117.40">
        <pitch>
          <step>G</step>
          <octave>2</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>up</stem>
        <notations>
          <articulations>
            <tenuto/>
            </articulations>
          </notations>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      </measure>
    <measure number="9" width="95.27">
      <note>
        <rest measure="yes"/>
        <duration>6</duration>
        <voice>1</voice>
        </note>
      </measure>
    <measure number="10" width="119.26">
      <direction placement="below">
        <direction-type>
          <dynamics default-x="3.25" default-y="-40.00" relative-y="-25.00">
            <p/>
            </dynamics>
          </direction-type>
        <sound dynamics="54.44"/>
        </direction>
      <note default-x="13.00" default-y="-77.40">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>4</duration>
        <voice>1</voice>
        <type>half</type>
        <stem>down</stem>
        <notations>
          <slur type="start" placement="above" number="1"/>
          </notations>
        </note>
      <note default-x="82.64" default-y="-77.40">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      </measure>
    <measure number="11" width="122.76">
      <note default-x="16.50" default-y="-82.40">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="start" placement="above" number="1"/>
          </notations>
        </note>
      <note default-x="51.32" default-y="-87.40">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        </note>
      <note default-x="86.14" default-y="-82.40">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      </measure>
    <measure number="12" width="133.96">
      <note default-x="16.50" default-y="-67.40">
        <pitch>
          <step>C</step>
          <octave>4</octave>
          </pitch>
        <duration>4</duration>
        <voice>1</voice>
        <type>half</type>
        <stem>down</stem>
        <notations>
          <slur type="start" placement="above" number="1"/>
          </notations>
        </note>
      <note default-x="93.61" default-y="-72.40">
        <pitch>
          <step>B</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      </measure>
    <measure number="13" width="193.18">
      <print new-system="yes">
        <staff-layout number="1">
          <staff-distance>35.00</staff-distance>
          </staff-layout>
        </print>
      <note default-x="96.87" default-y="-70.00">
        <pitch>
          <step>B</step>
          <alter>-1</alter>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <accidental>flat</accidental>
        <stem>down</stem>
        <notations>
          <slur type="start" placement="above" number="1"/>
          </notations>
        </note>
      <note default-x="128.37" default-y="-75.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        </note>
      <note default-x="159.87" default-y="-80.00">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      </measure>
    <measure number="14" width="112.81">
      <note default-x="16.50" default-y="-85.00">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      <note default-x="79.51" default-y="-95.00">
        <pitch>
          <step>D</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        </note>
      </measure>
    <measure number="15" width="93.27">
      <note default-x="20.96" default-y="-100.00">
        <pitch>
          <step>C</step>
          <alter>1</alter>
          <octave>3</octave>
          </pitch>
        <duration>4</duration>
        <voice>1</voice>
        <type>half</type>
        <accidental>sharp</accidental>
        <stem>up</stem>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      </measure>
    <measure number="16" width="181.36">
      <note default-x="13.00" default-y="-95.00">
        <pitch>
          <step>D</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      </measure>
    <measure number="17" width="94.42">
      <note default-x="16.50" default-y="-70.00">
        <pitch>
          <step>B</step>
          <octave>3</octave>
          </pitch>
        <duration>4</duration>
        <voice>1</voice>
        <type>half</type>
        <stem>down</stem>
        </note>
      <note default-x="63.34" default-y="-80.00">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      </measure>
    <measure number="18" width="112.81">
      <note default-x="16.50" default-y="-75.00">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="48.00" default-y="-95.00">
        <pitch>
          <step>D</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="79.51" default-y="-95.00">
        <pitch>
          <step>D</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      </measure>
    <measure number="19" width="172.00">
      <note default-x="16.50" default-y="-130.00">
        <pitch>
          <step>D</step>
          <octave>2</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>up</stem>
        <notations>
          <articulations>
            <tenuto/>
            </articulations>
          </notations>
        </note>
      <note default-x="60.22" default-y="-95.00">
        <pitch>
          <step>D</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="114.88" default-y="-95.00">
        <pitch>
          <step>D</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      </measure>
    <measure number="20" width="241.11">
      <print new-system="yes">
        <staff-layout number="1">
          <staff-distance>37.40</staff-distance>
          </staff-layout>
        </print>
      <note default-x="81.11" default-y="-82.40">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <tenuto/>
            </articulations>
          </notations>
        </note>
      <note default-x="126.31" default-y="-117.40">
        <pitch>
          <step>G</step>
          <octave>2</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>up</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="182.81" default-y="-117.40">
        <pitch>
          <step>G</step>
          <octave>2</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>up</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      </measure>
    <measure number="21" width="194.90">
      <note default-x="16.50" default-y="-117.40">
        <pitch>
          <step>G</step>
          <octave>2</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>up</stem>
        <beam number="1">begin</beam>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="45.93" default-y="-117.40">
        <pitch>
          <step>G</step>
          <octave>2</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>up</stem>
        <beam number="1">end</beam>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="75.37" default-y="-107.40">
        <pitch>
          <step>B</step>
          <octave>2</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>up</stem>
        <beam number="1">begin</beam>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="104.80" default-y="-97.40">
        <pitch>
          <step>D</step>
          <octave>3</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>up</stem>
        <beam number="1">end</beam>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="134.23" default-y="-82.40">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">begin</beam>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="163.67" default-y="-97.40">
        <pitch>
          <step>D</step>
          <octave>3</octave>
          </pitch>
        <duration>1</duration>
        <voice>1</voice>
        <type>eighth</type>
        <stem>down</stem>
        <beam number="1">end</beam>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      </measure>
    <measure number="22" width="142.10">
      <note default-x="35.69" default-y="-77.40">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <accent/>
            </articulations>
          </notations>
        </note>
      <note default-x="70.56" default-y="-97.40">
        <pitch>
          <step>D</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="105.43" default-y="-97.40">
        <pitch>
          <step>D</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      </measure>
    <measure number="23" width="176.50">
      <note default-x="16.50" default-y="-132.40">
        <pitch>
          <step>D</step>
          <octave>2</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>up</stem>
        <notations>
          <articulations>
            <accent/>
            </articulations>
          </notations>
        </note>
      <note default-x="61.70" default-y="-87.40">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="118.20" default-y="-87.40">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      </measure>
    <measure number="24" width="119.41">
      <note default-x="13.00" default-y="-117.40">
        <pitch>
          <step>G</step>
          <octave>2</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>up</stem>
        <notations>
          <articulations>
            <tenuto/>
            </articulations>
          </notations>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      </measure>
    <measure number="25" width="85.82">
      <direction placement="below">
        <direction-type>
          <dynamics default-x="3.25" default-y="-40.00" relative-y="-25.00">
            <p/>
            </dynamics>
          </direction-type>
        <sound dynamics="54.44"/>
        </direction>
      <note default-x="13.00" default-y="-82.40">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>6</duration>
        <voice>1</voice>
        <type>half</type>
        <dot/>
        <stem>down</stem>
        </note>
      </measure>
    <measure number="26" width="165.46">
      <print new-system="yes">
        <staff-layout number="1">
          <staff-distance>49.03</staff-distance>
          </staff-layout>
        </print>
      <note default-x="81.11" default-y="-89.03">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>4</duration>
        <voice>1</voice>
        <type>half</type>
        <stem>down</stem>
        <notations>
          <slur type="start" placement="above" number="1"/>
          </notations>
        </note>
      <note default-x="131.91" default-y="-94.03">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="start" placement="above" number="2"/>
          </notations>
        </note>
      </measure>
    <measure number="27" width="123.71">
      <note default-x="20.96" default-y="-94.03">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="stop" number="1"/>
          <slur type="stop" number="2"/>
          </notations>
        </note>
      <note default-x="54.61" default-y="-99.03">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        </note>
      <note default-x="88.26" default-y="-104.03">
        <pitch>
          <step>E</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        </note>
      </measure>
    <measure number="28" width="123.71">
      <note default-x="20.96" default-y="-109.03">
        <pitch>
          <step>D</step>
          <alter>1</alter>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <accidental>sharp</accidental>
        <stem>down</stem>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      </measure>
    <measure number="29" width="91.75">
      <note default-x="13.00" default-y="-119.03">
        <pitch>
          <step>B</step>
          <octave>2</octave>
          </pitch>
        <duration>4</duration>
        <voice>1</voice>
        <type>half</type>
        <stem>up</stem>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      </measure>
    <measure number="30" width="115.75">
      <note default-x="13.00" default-y="-114.03">
        <pitch>
          <step>C</step>
          <octave>3</octave>
          </pitch>
        <duration>4</duration>
        <voice>1</voice>
        <type>half</type>
        <stem>up</stem>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      </measure>
    <measure number="31" width="131.98">
      <note default-x="18.04" default-y="-109.03">
        <pitch>
          <step>D</step>
          <octave>3</octave>
          </pitch>
        <duration>4</duration>
        <voice>1</voice>
        <type>half</type>
        <accidental>natural</accidental>
        <stem>down</stem>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      </measure>
    <measure number="32" width="115.75">
      <note default-x="13.00" default-y="-129.03">
        <pitch>
          <step>G</step>
          <octave>2</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>up</stem>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      </measure>
    <measure number="33" width="91.75">
      <direction placement="below">
        <direction-type>
          <dynamics default-x="3.25" default-y="-40.00" relative-y="-25.00">
            <mp/>
            </dynamics>
          </direction-type>
        <sound dynamics="71.11"/>
        </direction>
      <note default-x="13.00" default-y="-94.03">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>4</duration>
        <voice>1</voice>
        <type>half</type>
        <stem>down</stem>
        <notations>
          <slur type="start" placement="above" number="1"/>
          </notations>
        </note>
      <note default-x="60.35" default-y="-99.03">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      </measure>
    <measure number="34" width="195.25">
      <print new-system="yes">
        <staff-layout number="1">
          <staff-distance>56.19</staff-distance>
          </staff-layout>
        </print>
      <direction placement="below">
        <direction-type>
          <wedge type="crescendo" number="1" default-y="-65.05"/>
          </direction-type>
        </direction>
      <note default-x="81.11" default-y="-111.19">
        <pitch>
          <step>E</step>
          <octave>3</octave>
          </pitch>
        <duration>4</duration>
        <voice>1</voice>
        <type>half</type>
        <stem>down</stem>
        <notations>
          <slur type="start" placement="above" number="1"/>
          </notations>
        </note>
      <note default-x="150.24" default-y="-116.19">
        <pitch>
          <step>D</step>
          <alter>1</alter>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <accidental>sharp</accidental>
        <stem>down</stem>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      <direction placement="below">
        <direction-type>
          <wedge type="stop" number="1"/>
          </direction-type>
        </direction>
      </measure>
    <measure number="35" width="113.11">
      <direction placement="below">
        <direction-type>
          <dynamics default-x="3.25" default-y="-45.05" relative-y="-25.00">
            <mf/>
            </dynamics>
          </direction-type>
        <sound dynamics="88.89"/>
        </direction>
      <direction placement="below">
        <direction-type>
          <wedge type="diminuendo" number="1" default-y="-65.05"/>
          </direction-type>
        </direction>
      <note default-x="16.50" default-y="-96.19">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>4</duration>
        <voice>1</voice>
        <type>half</type>
        <stem>down</stem>
        <notations>
          <slur type="start" placement="above" number="1"/>
          </notations>
        </note>
      <note default-x="74.84" default-y="-101.19">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      </measure>
    <measure number="36" width="104.01">
      <note default-x="13.00" default-y="-106.19">
        <pitch>
          <step>F</step>
          <alter>1</alter>
          <octave>3</octave>
          </pitch>
        <duration>4</duration>
        <voice>1</voice>
        <type>half</type>
        <stem>down</stem>
        <notations>
          <slur type="start" placement="above" number="1"/>
          </notations>
        </note>
      <note default-x="67.90" default-y="-111.19">
        <pitch>
          <step>E</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <slur type="stop" number="1"/>
          </notations>
        </note>
      <direction placement="below">
        <direction-type>
          <wedge type="stop" number="1"/>
          </direction-type>
        </direction>
      </measure>
    <measure number="37" width="128.00">
      <direction placement="below">
        <direction-type>
          <dynamics default-x="3.25" default-y="-45.05" relative-y="-25.00">
            <p/>
            </dynamics>
          </direction-type>
        <sound dynamics="54.44"/>
        </direction>
      <direction placement="below">
        <direction-type>
          <wedge type="crescendo" number="1" default-y="-65.05"/>
          </direction-type>
        </direction>
      <note default-x="13.00" default-y="-101.19">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="50.73" default-y="-101.19">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="88.47" default-y="-101.19">
        <pitch>
          <step>G</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <direction placement="below">
        <direction-type>
          <wedge type="stop" number="1"/>
          </direction-type>
        </direction>
      </measure>
    <measure number="38" width="131.50">
      <note default-x="16.50" default-y="-96.19">
        <pitch>
          <step>A</step>
          <octave>3</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>down</stem>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      </measure>
    <measure number="39" width="151.14">
      <note default-x="13.00" default-y="-126.19">
        <pitch>
          <step>B</step>
          <octave>2</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>up</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="58.45" default-y="-126.19">
        <pitch>
          <step>B</step>
          <octave>2</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>up</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      <note default-x="103.89" default-y="-126.19">
        <pitch>
          <step>B</step>
          <octave>2</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>up</stem>
        <notations>
          <articulations>
            <staccato/>
            </articulations>
          </notations>
        </note>
      </measure>
    <measure number="40" width="136.85">
      <note default-x="13.00" default-y="-136.19">
        <pitch>
          <step>G</step>
          <octave>2</octave>
          </pitch>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        <stem>up</stem>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      <note>
        <rest/>
        <duration>2</duration>
        <voice>1</voice>
        <type>quarter</type>
        </note>
      <barline location="right">
        <bar-style>light-heavy</bar-style>
        </barline>
      </measure>
    </part>
  </score-partwise>`,
  };
  
export default scoresData;
  