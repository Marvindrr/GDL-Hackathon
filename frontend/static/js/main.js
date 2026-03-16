document.addEventListener('DOMContentLoaded', function () {
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    var map = L.map('map').setView([21.8853, -102.2916], 12);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    var currentMarker = null;
    var currentCircle = null;
    var allMarkers = [];
    var allCircles = [];
    var routingControl = null;  


    function clearMap() {
        if (allMarkers.length > 0) {
            allMarkers.forEach(function(marker) {
                map.removeLayer(marker);  
            });
            allMarkers = [];  
        }
    
        if (allCircles.length > 0) {
            allCircles.forEach(function(circle) {
                map.removeLayer(circle);  
            });
            allCircles = [];  
        }
    
        if (routingControl) {
            map.removeControl(routingControl); 
            routingControl = null;  
        }
    
        
    }
    




    document.getElementById('search_input').oninput = function () {
        var query = document.getElementById('search_input').value;
        socket.emit('search', query); 
    };

    socket.on('search_results', function (results) {
        clearMap(); 

        var resultsDiv = document.getElementById('search_results');
        resultsDiv.innerHTML = '';  

        if (results.length === 0) {
            resultsDiv.innerHTML = '<p>No se encontraron colonias.</p>';
        } else {
            var ul = document.createElement('ul');
            results.forEach(function (colonia) {
                var li = document.createElement('li');
                li.textContent = colonia.nombre_colonia; 
                ul.appendChild(li);

                li.addEventListener('click', function () {
                    var lat = colonia.centro[1]; 
                    var lng = colonia.centro[0];
                    var riesgo =colonia.riesgo;

                    clearMap();
                    let randomNumber = Math.floor(Math.random() * 101);
                    currentMarker = L.marker([lat, lng]).addTo(map)
                    
                        .bindPopup(colonia.nombre_colonia + "<br>Riesgo: " + riesgo + "%")
                        .openPopup();

                    map.setView([lat, lng], 16);
                    allMarkers.push(currentMarker);

                    document.getElementById('route_button').style.display = 'block';

                    currentMarker.latlng = [lat, lng];
                });
            });
            resultsDiv.appendChild(ul);
        }
    });

    function LatLng(a) {
        const lat = a[1];  // latitud
        const lon =a[2];  // longitud

           
        const coordenadas = { lat: lat, lon: lon };
        return coordenadas;
    }
    var maxMaps = 4; 

    document.getElementById('route_button').onclick = function () {
        if (currentMarker) {
            var latlng = currentMarker.getLatLng(); 
    
            clearMap();
    
            currentCircle = L.circle(latlng, {
                color: 'red',
                fillColor: '#ff0000',
                fillOpacity: 0.3,
                radius: 1000
            }).addTo(map);
    
            allCircles.push(currentCircle);
            //console.log(latlng+"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
           
           
            coordenadas=LatLng(latlng);
           
    
            
            socket.emit('enviar_coordenadas', latlng);
            
    
            socket.on('camaras_cercanas', function(camaras) {

                console.log('Cámaras cercanas:', camaras);
               
                socket.on('camaras_cercanas', (camaras) => {
                    camaras.forEach(camara => {
                        if (camara.lat !== undefined && camara.lon !== undefined) {
                           
                            const lat = camara.lat;
                            const lng = camara.lon;
                
                        
                            if (lat && lng) {
                                let marker = L.marker([lat, lng], {
                                    icon: L.icon({
                                        iconUrl: 'https://cdn-icons-png.freepik.com/512/8335/8335224.png',
                                        iconSize: [30, 30],
                                        iconAnchor: [15, 30]
                                    })
                                }).addTo(map).bindPopup(`<b><a href="/camara" >${camara.id}</a></b>`);

                                allMarkers.push(marker);  // Asegúrate de añadir el marcador a allMarkers
                            } else {
                                console.error("Cámara no tiene coordenadas válidas:", camara);
                            }

                        } else {
                            console.error("Cámara no tiene coordenadas válidas:", camara);
                        }
                    });
                });
                
            });
    
           
            var destinos = [
                {lat: latlng.lat + 0.01, lng: latlng.lng + 0.01},  
                {lat: latlng.lat - 0.01, lng: latlng.lng - 0.01},  
                {lat: latlng.lat + 0.01, lng: latlng.lng - 0.01},  
                {lat: latlng.lat - 0.01, lng: latlng.lng + 0.01}   
            ];
    
            for (let i = 0; i < destinos.length; i++) {
                generateRoute(latlng, destinos[i], i + 1);
            }
        } else {
            console.log("No hay marcador actual.");
        }
    };

    
    function generateRoute(latlng, destino, mapIndex) {
        var mapDivId = "map" + mapIndex;
        var directionsDivId = "directions" + mapIndex;
        
        var mapDiv = document.getElementById(mapDivId);
        var directionsDiv = document.getElementById(directionsDivId);
        var tabla = document.getElementById('mapTable');
    
           
        mapDiv.innerHTML = '';
        directionsDiv.innerHTML = '';
    
        var newMap = L.map(mapDivId).setView([latlng.lat, latlng.lng], 13);
    
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(newMap);
    
        var routingControl = L.Routing.control({
            waypoints: [
                L.latLng(latlng.lat, latlng.lng), 
                L.latLng(destino.lat, destino.lng) 
            ],
            routeWhileDragging: true,
            createMarker: function() { return null; }, 
        }).addTo(newMap);
    
        routingControl.on('routesfound', function (e) {
            var routes = e.routes;
            var instructions = routes[0].instructions;
                
    
            directionsDiv.innerHTML = '';
    
            instructions.forEach(instruction => {
                var directionItem = document.createElement('div');
                directionItem.innerText = instruction.text;
                directionsDiv.appendChild(directionItem);
            });
    
            var summary = routes[0].summary;
            
            
            socket.emit('ruta_cambiada', {
                distancia: summary.totalDistance,  
                duracion: summary.totalTime,  
                waypoints: routes[0].coordinates, 
                calles: routes[0].instructions.map(instruction => instruction.text) 
            });
        });
    }
    
    

    document.getElementById('show_risk_areas_button').onclick = function () {
        clearMap();
        socket.emit('mostrar_zonas_riesgo');
    };

    socket.on('zonas_riesgo', function (zonas) {
        clearMap();
        zonas.forEach(function (zona) {
            
            let randomNumber = Math.floor(Math.random() * 101);
            const { nombre, lat, lng, riesgo } = zona;
            const color = obtenerColorRiesgo(riesgo);
        
            
            
            var circle = L.circle([lat, lng], {
                color: color,
                radius: 500,
                fillColor: color,
                fillOpacity: 0.5
            }).addTo(map);

            var marker = L.marker([lat, lng]).addTo(map)
                .bindPopup(`<b>${nombre}</b><br>Riesgo: ${riesgo}%`).openPopup();

            allCircles.push(circle);
            allMarkers.push(marker);
        });
    });

    function obtenerColorRiesgo(riesgo) {
        if (riesgo <= 30) return 'green';
        if (riesgo <= 60) return 'yellow';
        return 'red';
    }
});