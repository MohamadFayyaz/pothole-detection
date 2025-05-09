const MAP_SERVICE_API_KEY = 'Q4nI7ps7VqeivqwR5L8h';

export class CustomMap {
  zoom = 5;
  map = null;


  static async getPlaceNameByCoordinate(latitude, longitude) {
    try {
      const url = new URL(`https://api.maptiler.com/geocoding/${longitude},${latitude}.json`);
      url.searchParams.set('key', MAP_SERVICE_API_KEY);
      url.searchParams.set('language', 'id');
      url.searchParams.set('limit', '1');

      const response = await fetch(url);
      const json = await response.json();
      const place = json.features[0].place_name.split(', ');
      return [place.at(-2), place.at(-1)].join(', ');
    } catch (error) {
      console.error('getPlaceNameByCoordinate: error:', error);
      return `${latitude}, ${longitude}`;
    }
  }

  static isGeolocationAvailable() {
    return 'geolocation' in navigator;
  }

  static getCurrentPosition(options = {}) {
    return new Promise((resolve, reject) => {
      if (!CustomMap.isGeolocationAvailable()) {
        reject('Geolocation API unsupported');
        return;
      }
      navigator.geolocation.getCurrentPosition(resolve, reject, options);
    });
  }

  static async build(selector, options = {}) {
    if ('center' in options && options.center) {
      return new CustomMap(selector, options);
    }

    const indramayuCoordinate = [-6.327583, 108.324936];

    if ('locate' in options && options.locate) {
      try {
        const position = await CustomMap.getCurrentPosition();
        // const coordinate = [position.coords.latitude, position.coords.longitude];

        return new CustomMap(selector, {
          ...options,
          center: indramayuCoordinate,
        });
      } catch (error) {
        console.error('build: error:', error);

        return new CustomMap(selector, {
          ...options,
          center: indramayuCoordinate,
        });
      }
    }

    return new CustomMap(selector, {
      ...options,
      center: indramayuCoordinate,
    });
  }

  constructor(selector, options = {}) {
    this.zoom = options.zoom || this.zoom;
    // const mapContainer = document.querySelector(selector);
    // if (mapContainer._leaflet_id) {
    //   mapContainer._leaflet_id = null; // prevent double init
    // }
    this.map = L.map(document.querySelector(selector), {
      zoom: this.zoom,
      scrollWheelZoom: false,
      layers: [
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>',
        }),
      ],
      ...options,
    });
  }




  changeCamera(coordinate, zoomLevel = null) {
    // this.map.setView(L.latLng(coordinate), zoomLevel ?? this.zoom);
    if (!zoomLevel) {
      this.map.setView(latLng(coordinate), this.zoom);
      return;
    }
    this.map.setView(latLng(coordinate), zoomLevel);
  }

  getCenter() {
    const { lat, lng } = this.map.getCenter();
    return {
      latitude: lat,
      longitude: lng,
    };
  }

  get leafletMap() {
    return this.map;
  }

  createIcon(options = {}) {
    return L.icon({
      ...L.Icon.Default.prototype.options,
      iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
      iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
      shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
      ...options,
    });
  }

  addMarker(coordinates, markerOptions = {}, popupOptions = null) {
    const newMarker = L.marker(coordinates, {
      icon: this.createIcon(),
      ...markerOptions,
    });

    // Jika ada popupOptions, bind popup ke marker
    if (popupOptions) {
      newMarker.bindPopup(popupOptions.content);
    }

    newMarker.addTo(this.map);
    return newMarker;
  }

  addMapEventListener(eventName, callback) {
    this.map.on(eventName, callback);
  }
}

// Contoh penggunaan
// (async () => {
//   const myMap = await CustomMap.build('#map', { locate: true, zoom: 10 });
//   myMap.addMapEventListener('click', async (e) => {
//     const lat = e.latlng.lat;
//     const lng = e.latlng.lng;

//     const locationName = await CustomMap.getPlaceNameByCoordinate(lat, lng);

//     myMap.addMarker([lat, lng], {}, {
//       content: `Lokasi: ${locationName}`
//     });
//   });
// })();