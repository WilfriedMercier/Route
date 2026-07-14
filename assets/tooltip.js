window.dashMantineFunctions = window.dashMantineFunctions || {};

window.dashMantineFunctions.roundNumber = function(number) {
    return number.toFixed(1);
};

window.dashMantineFunctions.CustomTooltip = function(props) {
    if (!props.active || !props.payload || !props.payload.length) {
        return null;
    }
    
    // Extract values
    var distance = props.label;
    var elevation = props.payload[0].value;
    var color = 'var(--custom-theme-color)' || '#6d4aff';
    
    // Create tooltip element using React.createElement
    return React.createElement('div', {
        style: {
            backgroundColor: '#fff',
            border: '1px solid #ccc',
            borderRadius: '4px',
            padding: '10px 12px',
            fontSize: '12px',
            fontFamily: '-apple-system, BlinkMacSystemFont, sans-serif',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }
    }, [
        React.createElement('div', {
            key: 'distance',
            style: { marginBottom: '4px' }
        }, 
            React.createElement('span', {style : {color: '#000000'}}, 'Distance: '),
            React.createElement('strong', { style: { color: color } }, distance.toFixed(1) + ' km')
        ),
        React.createElement('div', {
            key: 'elevation',
            style: {}
        },
            React.createElement('span', {style : {color: '#000000'}}, 'Elevation: '),
            React.createElement('strong', { style: { color: color } }, Math.round(elevation) + ' m')
        )
    ]);
};