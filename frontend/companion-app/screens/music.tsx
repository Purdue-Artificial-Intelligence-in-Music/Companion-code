import { musicxml } from "music21j";
import {useState, useRef} from "react"

export default function Music21jEx() {
    const [musicData, setMusicData] = useState(null);
    const svgContainerRef = useRef(null);
    const parser = new musicxml.xmlToM21.ScoreParser()
    const mxUrl = '../assets/air_on_the_g_string.musicxml'
    let scoreObject;
    parser.scoreFromUrl(mxUrl).then(sc => {
        scoreObject = sc;
        if (svgContainerRef.current) { // Ensure ref is not null
            sc.appendNewDOM(svgContainerRef.current);
          }
        }).catch((error) => {
          console.error("Error rendering score:", error);
    });
    return (
        <div>
        <p>Music21j Display</p>
        <div ref={svgContainerRef}></div>
        </div>
    )
}