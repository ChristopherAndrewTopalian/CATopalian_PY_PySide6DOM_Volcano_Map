# CATopalian_PY_PySide6DOM_Volcano_Map.pyw

import urllib.request
import json
import os
from pyside6dom import *

my_icon = os.path.join("src", "media", "textures", "icons", "001.png")

init_window('CATopalian PY PySide6DOM Volcano Map', 1000, 800, my_icon)

set_theme('''
    body {
        background-color: rgb(20, 20, 25);
        color: white;
        font-family: 'Segoe UI', Arial; 
        margin: 0px;
        padding: 0px;
    }
    .map_canvas {
        background-color: rgb(30, 35, 45); 
        border-bottom: 3px solid rgb(100, 100, 120);
    }
    .volcano_dot {
        background-color: rgba(255, 140, 0, 0.8); /* Magma Orange */
        border-radius: 50%; /* Make them perfectly round */
    }
    .list_row {
        padding: 10px;
        border-bottom: 1px solid #444;
    }
    .list_row:hover {
        background-color: #333;
    }
    .volcano_badge {
        background-color: #ff6600;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
        margin-right: 10px;
    }
''')

MAP_WIDTH = 1000
MAP_HEIGHT = 500

# ===
# UI LAYOUT
# ===
header = ce('div')
header.style.backgroundColor = 'rgb(15, 15, 20)'
header.style.padding = 10
header.style.display = 'flex'
header.style.flexDirection = 'row'
header.style.alignItems = 'center'
ba(header)

app_title = ce('h2')
app_title.textContent = "Active Volcanoes"
app_title.style.color = '#ffcc00'
header.append(app_title)

# We give it an ID so we can update it after the data loads
count_lbl = ce('h3')
count_lbl.id = 'count_lbl'
count_lbl.textContent = "Scanning seismic data..."
count_lbl.style.color = '#ff6600'
count_lbl.style.marginLeft = '20px'
header.append(count_lbl)

# Top Half: The Map
map_view = ce('div')
map_view.className = 'map_canvas'
map_view.style.width = MAP_WIDTH
map_view.style.height = MAP_HEIGHT
map_view.style.position = 'relative' 
ba(map_view)

# Add the Map Image Background
map_bg = ce('img')
map_bg.src = os.path.join("src", "media", "textures", "maps", "Earthmap1000x500.jpg")
map_bg.style.position = 'absolute'
map_bg.style.left = 0
map_bg.style.top = 0
map_bg.width = MAP_WIDTH
map_bg.height = MAP_HEIGHT
map_view.append(map_bg)

# Bottom Half: The Data List
list_view = ce('scroll_div')
list_view.style.width = MAP_WIDTH
list_view.style.height = 300
list_view.style.padding = 10
ba(list_view)

# ===
# THE MATH 
# ===
def lat_lon_to_xy(lat, lon):
    x = (lon + 180.0) * (MAP_WIDTH / 360.0)
    y = (90.0 - lat) * (MAP_HEIGHT / 180.0)
    return x, y

# ===
# FETCH AND PLOT DATA
# ===
def load_volcanoes():
    # GDACS Live Search API for Volcanoes (VO)
    url = "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH?eventlist=VO"
    
    # a header
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        response = urllib.request.urlopen(req)
        data = json.loads(response.read())
        features = data.get('features', [])
        
        # Update the UI with the exact count
        if len(features) == 0:
            ge('count_lbl').textContent = "No active major eruptions."
        else:
            ge('count_lbl').textContent = f"Active Eruptions: {len(features)}"

        for volcano in features:
            props = volcano['properties']
            coords = volcano['geometry']['coordinates'] 
            
            # Using .get() as our safety net
            name = props.get('name', 'Unnamed Volcano')
            alert_level = props.get('alertlevel', 'VO') 
            
            lon = coords[0]
            lat = coords[1]

            # Draw the Dot
            x, y = lat_lon_to_xy(lat, lon)

            dot = ce('div')
            # Add the Rich Text Tooltip
            dot.title = f"<b>{name}</b><br>Alert Level: {alert_level}"
            dot.titleFontSize = "16px"
            dot.className = 'volcano_dot'
            dot.style.position = 'absolute'
            dot.style.left = int(x) - 6
            dot.style.top = int(y) - 6
            
            size = 12 
            dot.style.width = size
            dot.style.height = size
            map_view.append(dot)

            # Draw the Row
            row = ce('div')
            row.className = 'list_row'
            row.style.display = 'flex'
            row.style.flexDirection = 'row'
            row.style.alignItems = 'center'
            row.raw.setCursor(Qt.CursorShape.PointingHandCursor)

            badge = ce('text')
            badge.className = 'volcano_badge'
            badge.textContent = "VOLCANO"
            badge.raw.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents) # Ghost fix
            row.append(badge)

            info = ce('text')
            info.textContent = name
            info.style.fontSize = '16px'
            info.raw.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents) # Ghost fix
            row.append(info)

            list_view.append(row)

            # ===
            # THE HOVER & CLICK INTERACTIVITY
            # ===
            def hover_in(d=dot, r=row, s=size, px=x, py=y):
                d.style.backgroundColor = 'rgb(255, 255, 0)' # Bright yellow on hover
                d.style.width = s + 6
                d.style.height = s + 6
                # Shift left and up by 3 pixels to stay centered
                d.style.left = int(px) - 6 - 3  
                d.style.top = int(py) - 6 - 3
                d.style.border = '2px solid white'
                d.raw.raise_() 
                r.style.backgroundColor = '#444'

            def hover_out(d=dot, r=row, s=size, px=x, py=y):
                d.style.backgroundColor = 'rgba(255, 140, 0, 0.8)' # Return to magma
                d.style.width = s
                d.style.height = s
                # Return the dot to its original position
                d.style.left = int(px) - 6
                d.style.top = int(py) - 6
                d.style.border = 'none'
                r.style.backgroundColor = 'transparent'

            def open_maps(lt=lat, ln=lon):
                url = f"https://www.google.com/maps/search/?api=1&query={lt},{ln}"
                QDesktopServices.openUrl(QUrl(url))

            row.addEventListener('mouseenter', hover_in)
            row.addEventListener('mouseleave', hover_out)
            row.onclick = open_maps
            
            dot.raw.setCursor(Qt.CursorShape.PointingHandCursor)
            dot.addEventListener('mouseenter', hover_in)
            dot.addEventListener('mouseleave', hover_out)
            dot.onclick = open_maps

    except Exception as e:
        print(f"Failed to load volcano data: {e}")

load_volcanoes()
run_app()

####

# Dedicated to God the Father
# (c) Copyright 2026 Christopher Andrew Topalian All Rights Reserved
# https://github.com/ChristopherTopalian
# https://github.com/ChristopherAndrewTopalian
# https://sites.google.com/view/CollegeOfScripting

