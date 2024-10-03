// MusicXMLViewer.js
import React, { useEffect, useRef } from 'react';
import { View } from 'react-native';
import { OpenSheetMusicDisplay } from 'opensheetmusicdisplay';

interface MusicXMLViewerProps {
    xmlData: string;
}

const MusicXMLViewer: React.FC<MusicXMLViewerProps> = ({ xmlData }) => {
    const osmdRef = useRef<OpenSheetMusicDisplay | null>(null);

    useEffect(() => {
        if (osmdRef.current) {
            osmdRef.current.load(xmlData);
            osmdRef.current.render();
        }
    }, [xmlData]);

    const setRef = (element: HTMLDivElement | null) => {
        if (element && !osmdRef.current) {
            osmdRef.current = new OpenSheetMusicDisplay(element);
            osmdRef.current.load(xmlData);
            osmdRef.current.render();
        }
    };

    return (
        <View style={{ flex: 1 }}>
            <div ref={setRef}></div>
        </View>
    );
};

export default MusicXMLViewer;
