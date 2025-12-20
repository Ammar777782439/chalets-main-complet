from django import forms
from django.utils.safestring import mark_safe


class LocationPickerWidget(forms.Widget):
    """
    Custom widget for selecting location coordinates using an interactive map.
    Uses OpenStreetMap with Leaflet for map functionality.
    """
    
    def format_value(self, value):
        if value:
            if isinstance(value, (list, tuple)) and len(value) >= 3:
                return {'latitude': value[0], 'longitude': value[1], 'address': value[2]}
            elif isinstance(value, dict):
                return value
        return {'latitude': None, 'longitude': None, 'address': None}
    
    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        
        # Format the value
        formatted_value = self.format_value(value)
        
        # Generate unique IDs
        widget_id = attrs.get('id', name)
        map_id = f"map_{widget_id}"
        
        # Create the HTML
        html = f"""
        <div class="location-picker-widget" id="{widget_id}_container">
            <div class="form-row">
                <label>العنوان:</label>
                <input type="text" name="{name}_address" id="{widget_id}_address" 
                       value="{formatted_value.get('address', '') or ''}" 
                       placeholder="أدخل العنوان" style="width: 100%; padding: 8px; margin: 5px 0;">
            </div>
            
            <div class="form-row">
                <label>الإحداثيات:</label>
                <div style="display: flex; gap: 10px; margin: 5px 0;">
                    <input type="text" id="{widget_id}_lat_display" placeholder="خط العرض" 
                           readonly style="width: 150px; padding: 5px;">
                    <input type="text" id="{widget_id}_lng_display" placeholder="خط الطول" 
                           readonly style="width: 150px; padding: 5px;">
                    <button type="button" onclick="clearLocation_{map_id}()" 
                            style="padding: 5px 10px; background: #dc3545; color: white; border: none; border-radius: 3px;">مسح</button>
                </div>
            </div>
            
            <div class="form-row">
                <label>اختر الموقع من الخريطة:</label>
                <div id="{map_id}" style="height: 400px; width: 100%; border: 1px solid #ccc; margin: 10px 0;"></div>
            </div>
            
            <input type="hidden" name="{name}" id="{widget_id}" 
                   value="{formatted_value.get('latitude', '') or ''},{formatted_value.get('longitude', '') or ''},{formatted_value.get('address', '') or ''}">
        </div>
        
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            if (typeof L === 'undefined') {{
                // Load Leaflet if not already loaded
                var link = document.createElement('link');
                link.rel = 'stylesheet';
                link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
                document.head.appendChild(link);
                
                var script = document.createElement('script');
                script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
                script.onload = function() {{
                    setTimeout(function() {{
                        initMap_{map_id}();
                    }}, 100);
                }};
                document.head.appendChild(script);
            }} else {{
                setTimeout(function() {{
                    initMap_{map_id}();
                }}, 100);
            }}
        }});
        
        function initMap_{map_id}() {{
            try {{
                // Initialize map
                var map_{map_id} = L.map('{map_id}').setView([15.3694, 44.1910], 7);
                
                // Add OpenStreetMap tiles
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '© OpenStreetMap contributors'
                }}).addTo(map_{map_id});
                
                var marker_{map_id} = null;
                
                // Get form elements
                var hiddenInput = document.getElementById('{widget_id}');
                var addrInput = document.getElementById('{widget_id}_address');
                var latDisplay = document.getElementById('{widget_id}_lat_display');
                var lngDisplay = document.getElementById('{widget_id}_lng_display');
                
                // Function to update marker and form fields
                function updateLocation(lat, lng, address) {{
                    if (marker_{map_id}) {{
                        map_{map_id}.removeLayer(marker_{map_id});
                    }}
                    
                    marker_{map_id} = L.marker([lat, lng]).addTo(map_{map_id});
                    
                    latDisplay.value = lat.toFixed(6);
                    lngDisplay.value = lng.toFixed(6);
                    hiddenInput.value = lat.toFixed(6) + ',' + lng.toFixed(6) + ',' + (address || '');
                    
                    if (address) {{
                        addrInput.value = address;
                    }}
                }}
                
                // Function to clear location
                window.clearLocation_{map_id} = function() {{
                    if (marker_{map_id}) {{
                        map_{map_id}.removeLayer(marker_{map_id});
                        marker_{map_id} = null;
                    }}
                    latDisplay.value = '';
                    lngDisplay.value = '';
                    addrInput.value = '';
                    hiddenInput.value = '';
                }};
                
                // Handle map clicks
                map_{map_id}.on('click', function(e) {{
                    var lat = e.latlng.lat;
                    var lng = e.latlng.lng;
                    
                    // Reverse geocoding to get address
                    fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${{lat}}&lon=${{lng}}&accept-language=ar`)
                        .then(response => response.json())
                        .then(data => {{
                            var address = data.display_name || '';
                            updateLocation(lat, lng, address);
                        }})
                        .catch(() => {{
                            updateLocation(lat, lng, '');
                        }});
                }});
                
                // Initialize with existing values
                var currentValue = hiddenInput.value;
                if (currentValue) {{
                    var parts = currentValue.split(',');
                    if (parts.length >= 2) {{
                        var lat = parseFloat(parts[0]);
                        var lng = parseFloat(parts[1]);
                        var address = parts.slice(2).join(',');
                        
                        if (!isNaN(lat) && !isNaN(lng)) {{
                            updateLocation(lat, lng, address);
                            map_{map_id}.setView([lat, lng], 15);
                        }}
                    }}
                }}
                
                // Handle address input for geocoding
                var geocodeTimeout;
                addrInput.addEventListener('input', function() {{
                    clearTimeout(geocodeTimeout);
                    geocodeTimeout = setTimeout(function() {{
                        var address = addrInput.value.trim();
                        if (address.length > 3) {{
                            fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${{encodeURIComponent(address)}}&limit=1&accept-language=ar`)
                                .then(response => response.json())
                                .then(data => {{
                                    if (data && data.length > 0) {{
                                        var lat = parseFloat(data[0].lat);
                                        var lng = parseFloat(data[0].lon);
                                        updateLocation(lat, lng, address);
                                        map_{map_id}.setView([lat, lng], 15);
                                    }}
                                }})
                                .catch(console.error);
                        }}
                    }}, 1000);
                }});
            }} catch (error) {{
                console.error('Error initializing map:', error);
            }}
        }}
        </script>
        
        <style>
        .location-picker-widget .form-row {{
            margin-bottom: 15px;
        }}
        .location-picker-widget label {{
            display: block;
            font-weight: bold;
            margin-bottom: 5px;
            color: #333;
        }}
        .location-picker-widget input[type="text"] {{
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 14px;
        }}
        .location-picker-widget button {{
            background-color: #dc3545;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }}
        .location-picker-widget button:hover {{
            background-color: #c82333;
        }}
        </style>
        """
        
        return mark_safe(html)
    
    def value_from_datadict(self, data, files, name):
        value = data.get(name)
        if value:
            parts = value.split(',')
            if len(parts) >= 2:
                try:
                    lat = float(parts[0]) if parts[0] else None
                    lng = float(parts[1]) if parts[1] else None
                    address = ','.join(parts[2:]) if len(parts) > 2 else ''
                    return [lat, lng, address]
                except (ValueError, IndexError):
                    pass
        return [None, None, None]
    
    class Media:
        css = {
            'all': ('https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',)
        }
        js = ('https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',)


class LocationPickerField(forms.Field):
    """
    Custom form field that combines latitude, longitude, and address
    with an interactive map widget.
    """
    widget = LocationPickerWidget
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def to_python(self, value):
        if not value or value == [None, None, None] or value == ['', '', '']:
            return [None, None, None]
        if isinstance(value, (list, tuple)):
            return list(value)
        return [None, None, None]
    
    def validate(self, value):
        # Skip validation for empty values since the field is not required
        if not value or value == [None, None, None]:
            return
        super().validate(value)