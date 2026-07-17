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
        },

        update_hover_marker : function (hoverdata, bbox, lat_lon, props) {

            // Custom marker on the map
            let path = document.getElementById('map-marker-js');

            if (!hoverdata || !bbox || !lat_lon) {
            
                if (path) {
                    path.setAttribute('stroke-opacity', '0');
                    path.setAttribute('fill-opacity',   '0');
                }
                
                return null;
            }

            const hike_svg = document.getElementsByClassName('leaflet-interactive');
            const map_pane = document.getElementsByClassName('leaflet-pane leaflet-map-pane');

            if (!hike_svg || !map_pane) {
                throw console.error('No leaflet interaction or map-pane object found.');
            }

            // Index of the hovered point in the array
            const index = hoverdata.points[0].pointIndex;

            // Find the bounding box in pixels of the map
            const map  = document.getElementById('map');
            const rect = map.getBoundingClientRect();

            // Extract transform 3D properties to add to x and y coordinates and convert them to a 2D float array
            let transform = map_pane[0].style
                            .transform
                            .split('translate3d(')[1]
                            .split(')')[0]
                            .split(',')
                            .slice(0, 2);

            transform     = transform.map((x) => parseFloat(x.split('px')));

            // Get the coordinates of the hovered point
            const lat       = lat_lon.latitudes[ index];
            const lon       = lat_lon.longitudes[index];
            
            // Transform the coordinates into pixel coordinates
            const delta_lat = bbox[1][0] - bbox[0][0];
            const delta_lon = bbox[1][1] - bbox[0][1];

            const x = (lon - bbox[0][1]) / delta_lon * rect.width - transform[0];
            const y = rect.height - (lat - bbox[0][0]) / delta_lat * rect.height - transform[1];

        
            // Create the SVG path element (must use NS for SVG) if if does not exist
            if (!path) {
            
                path = document.createElementNS('http://www.w3.org/2000/svg', 'path');

                path.setAttribute('class', 'leaflet-interactive');
                path.setAttribute('stroke-width', '3');
                path.setAttribute('stroke-linecap', 'round');
                path.setAttribute('stroke-linejoin', 'round');
                path.setAttribute('fill-rule', 'evenodd');
                path.setAttribute('id', 'map-marker-js');
                hike_svg[0].parentElement.appendChild(path);
            }

            // Update relevant path properties
            path.setAttribute('stroke', props['color']);
            path.setAttribute('fill', props['color']);
            path.setAttribute('fill-opacity', '0.2');
            path.setAttribute('stroke-opacity', '1');
            path.setAttribute('d', `M${x},${y}a6,6 0 1,0 12,0 a6,6 0 1,0 -12,0`);

            return null;
        }
    }
});