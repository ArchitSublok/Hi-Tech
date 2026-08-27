document.addEventListener('DOMContentLoaded', function () {
    const mapEl = document.getElementById('checkoutMap');
    if (!mapEl) return;

    const map = L.map('checkoutMap').setView([28.6139, 77.2090], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    let marker = L.marker([28.6139, 77.2090], { draggable: true }).addTo(map);

    function setFields(lat, lng, data) {
        document.getElementById('latField').value = lat;
        document.getElementById('lngField').value = lng;
        if (data && data.address) {
            const address = data.address;
            document.getElementById('streetField').value = [address.house_number, address.road].filter(Boolean).join(' ');
            document.getElementById('areaLocality').value = address.suburb || address.neighbourhood || address.quarter || '';
            document.getElementById('cityField').value = address.city || address.town || address.village || '';
            document.getElementById('stateField').value = address.state || '';
            document.getElementById('postalField').value = address.postcode || '';
        }
    }

    function reverseGeocode(lat, lng) {
        fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`)
            .then(res => res.json())
            .then(data => setFields(lat, lng, data))
            .catch(() => setFields(lat, lng, null));
    }

    marker.on('dragend', function () {
        const pos = marker.getLatLng();
        map.panTo(pos);
        reverseGeocode(pos.lat, pos.lng);
    });

    map.on('click', function (e) {
        marker.setLatLng(e.latlng);
        reverseGeocode(e.latlng.lat, e.latlng.lng);
    });

    const searchInput = document.getElementById('geocodeSearch');
    let searchTimeout;
    searchInput.addEventListener('input', function () {
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        if (query.length < 3) return;
        searchTimeout = setTimeout(function () {
            fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`)
                .then(res => res.json())
                .then(results => {
                    if (results.length) {
                        const lat = parseFloat(results[0].lat);
                        const lng = parseFloat(results[0].lon);
                        map.setView([lat, lng], 16);
                        marker.setLatLng([lat, lng]);
                        reverseGeocode(lat, lng);
                    }
                });
        }, 600);
    });

    const addressSelect = document.getElementById('addressSelect');
    const newAddressFields = document.getElementById('newAddressFields');
    function toggleNewAddressFields() {
        const needsNewAddress = !addressSelect || addressSelect.value === 'new';
        newAddressFields.hidden = !needsNewAddress;
        newAddressFields.querySelectorAll('input, textarea').forEach(function (field) {
            field.disabled = !needsNewAddress;
        });
        if (needsNewAddress) {
            window.setTimeout(function () { map.invalidateSize(); }, 0);
        }
    }

    if (addressSelect) {
        addressSelect.addEventListener('change', toggleNewAddressFields);
    }
    toggleNewAddressFields();
});
