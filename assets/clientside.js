window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {

        /**
        * Callback used whenever the slider moves.
        *
        * @param {numeric} index - index in the lat_lon or plot_data arrays used to identify the point highlighted by the slider
        * @param {Object} plot_data - object containing the distance array used to draw the vertical highlight line
        * @param {Object} lat_lon - contains two keys, latitudes and longitudes, each an array of floating values containing the coordinates of all the points on the path
        * @param {Object} bbox - latitude and longitude bounding box of the map
        * @param {Object} props - additional properties associated to the hike, in particular its color
        * @param {Object} dummy - dummy object whose n_clicks key is always incremented by one
        */
        slider_callback: function(index, plot_data, lat_lon, bbox, props, dummy) {

            if (!index || !plot_data || !lat_lon || !bbox || !props) {
                throw console.error('Missing input data to trigger the slider callback.');
            }

            const out_dummy = {'n_clicks' : dummy['n_clicks'] + 1, 'type' : 'slider_update'}

            // Get distance associated to index
            const distance = plot_data['distances'][index];

            // Get x position on screen of beginning and end of the xaxis
            const el   = document.getElementsByClassName('nsewdrag drag cursor-pointer');

            // Find the element that contains the crisp lines
            const hoverlayer = document.getElementsByClassName('hoverlayer');

            if (el && el.length > 0 && hoverlayer && hoverlayer.length > 0) {

                const init = el[0].x.baseVal.value;
                const width = el[0].width.baseVal.value;

                // Find the x position corresponding to the given distance
                const x = init + distance / plot_data['distances'].slice(-1) * width;

                if (x < 0 || x > init + width) {
                    return out_dummy;
                }

                // Update or create a line to show the position of the slider
                let line = document.getElementById('tooltip-vertical-line-mobile');
                
                // Create if non-existent
                if (!line) {
                    line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                    line.setAttribute('stroke-width', '3');
                    line.setAttribute('class', 'spikeline crisp');
                    line.setAttribute('id', 'tooltip-vertical-line-mobile');
                    hoverlayer[0].appendChild(line);
                }

                // Update position and color of the line
                line.setAttribute('stroke', 'rgb(255, 122, 255)');
                line.setAttribute('x1', x);
                line.setAttribute('x2', x);
                line.setAttribute('y1', '0');
                line.setAttribute('y2', '140');

                // Handle the hover marker

                // Get the coordinates of the hovered point
                const lat = lat_lon.latitudes[ index];
                const lon = lat_lon.longitudes[index];

                this.update_hover_marker(lat, lon, bbox, props);
            }

            return out_dummy;
        },

        /**
        * Callback used whenever the mouse hovers over the elevation plot.
        *
        * @param {Object} hoverdata - data passed by dash leaflet when the mouse hovers over the map
        * @param {number[]} bbox - latitude and longitude bounding box of the map
        * @param {Object} lat_lon - contains two keys, latitudes and longitudes, each an array of floating values containing the coordinates of all the points on the path
        * @param {Object} props - additional properties associated to the hike, in particular its color
        * @param {Object} dummy - dummy object whose n_clicks key is always incremented by one
        */
        elevation_plot_hover_callback: function (hoverdata, bbox, lat_lon, props, dummy) {

            let lat = null;
            let lon = null;

            if (hoverdata && bbox && lat_lon && props) {
                
                // Index of the hovered point in the array
                const index = hoverdata.points[0].pointIndex;

                // Get the coordinates of the hovered point
                lat = lat_lon.latitudes[ index];
                lon = lat_lon.longitudes[index];
            }

            this.update_hover_marker(lat, lon, bbox, props);
            return {'n_clicks' : dummy['n_clicks'] + 1, 'type' : 'elevation-plot-hover'}

        },

        /** 
         * Generic function used to update the position of the marker on the map.
         * 
         * @param {number} lat - latitude coordinate of the marker
         * @param {number} lon - longitude coordinate of the marker
         * @param {Object} bbox - latitude and longitude bounding box of the map
         * @param {Object} props - additional properties associated to the hike, in particular its color
         * @returns null
         */
        update_hover_marker : function (lat, lon, bbox, props) {

            // Custom marker on the map
            let path = document.getElementById('map-marker-js');

            // If input missing, the marker is hidden
            if (!lat || !lon || !bbox || !props) {
            
                if (path) {
                    path.setAttribute('stroke-opacity', '0');
                    path.setAttribute('fill-opacity',   '0');
                }
                
                throw console.error('Missing input data to update the hover marker.');
            }

            const hike_svg = document.getElementsByClassName('leaflet-interactive');
            const map_pane = document.getElementsByClassName('leaflet-pane leaflet-map-pane');

            if (!hike_svg || !map_pane) {
                throw console.error('No leaflet interaction or map-pane object found.');
            }

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
        },

        /** 
         * Callback used to hide the marker and the vertical line in the elevation plot when the map is zoomed in or out.
         * 
         * @param {number} zoom - zoom level
         * @param {Object} dummy - dummy object whose n_clicks key must always be incremented by one
         */
        hide_marker_and_highlight_line: function (zoom, dummy) {
            const path = document.getElementById('map-marker-js');
            
            if (path) {
                path.setAttribute('stroke-opacity', '0');
                path.setAttribute('fill-opacity',   '0');
            }

            const line = document.getElementById('tooltip-vertical-line-mobile');
            if (line) {
                line.setAttribute('stroke', 'rgb(0, 0, 0, 0)');
            }

            return {'n_clicks' : dummy['n_clicks'] + 1, 'type' : 'hide-marker-and-line'};
        }
    }
});