window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        mobile_slider_interaction: function(index, data) {

            // Get distance associated to index
            const distance = data['distances'][index];

            // Get x position on screen of beginning and end of the xaxis
            const el   = document.getElementsByClassName('nsewdrag drag cursor-pointer');

            // Find the element that contains the crisp lines
            const hoverlayer = document.getElementsByClassName('hoverlayer');

            if (el && el.length > 0 && hoverlayer && hoverlayer.length > 0) {

                const init = el[0].x.baseVal.value;
                const width = el[0].width.baseVal.value;

                // Find the x position corresponding to the given distance
                const x = init + distance / data['distances'].slice(-1) * width;

                if (x < 0 || x > init + width) {return null;}

                // Update or create a line to show the position of the slider
                let line = document.getElementById('tooltip-vertical-line-mobile');
                
                // Create if non-existent
                if (!line) {
                    line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                    line.setAttribute('stroke-width', '3');
                    line.setAttribute('stroke', 'rgb(255, 122, 255)');
                    line.setAttribute('class', 'spikeline crisp');
                    line.setAttribute('id', 'tooltip-vertical-line-mobile');
                    hoverlayer[0].appendChild(line);
                }

                // Update position of the line
                line.setAttribute('x1', x);
                line.setAttribute('x2', x);
                line.setAttribute('y1', '0');
                line.setAttribute('y2', '140');
                
            }

            return null;
        }
    }
});