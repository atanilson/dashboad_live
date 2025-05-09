import geopandas as gpd
import contextily as ctx
import matplotlib.pyplot as plt
import matplotlib.patches as legendp
import matplotlib.ticker as mticker

#Dashboar

from folium.plugins import MarkerCluster
import folium

import geopandas as gpd
import hvplot.pandas
import panel as pn

#Pie chart
from math import pi
from bokeh.palettes import Category20c, Category20
from bokeh.plotting import figure
from bokeh.transform import cumsum

# Serch Photo Park
from duckduckgo_search import DDGS

pn.extension()

#Delete
import pandas as pd
#import pandas_bokeh


# Importing protected area as parks0
parks0 = gpd.read_file("WDPA_WDOECM_Mar2025_Public_GBR_shp_0.zip")
uk_countries = gpd.read_file("Countries_December_2024_Boundaries_UK_BFC_6983126662299524946.zip") # Countries
uk_countries = uk_countries.to_crs(epsg=4326) # Geo


# After studying the data some names a repeted so mapping to unique names
parks0['DESIG_U'] = parks0['DESIG'].str.strip().str.lower()
unique_name = {
    'national park': 'National Park',
    'national nature reserve': 'National Nature Reserve',
    'unesco-mab biosphere reserve': 'UNESCO Biosphere Reserve',
    'heritage coast': 'Heritage Coast',
    'world heritage site (natural or mixed)': 'World Heritage Site',
    'national scenic area': 'National Scenic Area',
    'area of outstanding natural beauty': 'Area of Outstanding Natural Beauty',
    'regional park': 'Regional Park',
    'ramsar site, wetland of international importance': 'Ramsar Site',
    'area of special scientific interest': 'Site of Special Scientific Interest',
    'local nature reserve': 'Local Nature Reserve',
    'site of special scientific interest': 'Site of Special Scientific Interest',
    'site of special scientific interest (uk)': 'Site of Special Scientific Interest'
}
# Replacinf old name with unique names for each
parks0['DESIG_U'] = parks0['DESIG_U'].replace(unique_name)

# Assigning appropiate color for each park
colors = {
    'National Park': '#228B22',  # Forest Green
    'National Nature Reserve': '#6B8E23',  # Olive Drab
    'UNESCO Biosphere Reserve': '#20B2AA',# Light Sea Green
    'Heritage Coast': '#F4A460',# Sandy Brown
    'World Heritage Site': '#9370DB',# Medium Purple
    'National Scenic Area': '#4682B4',# Steel Blue
    'Area of Outstanding Natural Beauty': '#3CB371',# Medium Sea Green
    'Regional Park': '#008B8B',# Dark Cyan
    'Ramsar Site': '#87CEEB',# Sky Blue
    'Site of Special Scientific Interest': '#DAA520',# Goldenrod
    'Local Nature Reserve': '#32CD32'# Lime Green
}

#UK land Protected area
parks2 = gpd.read_file("WDPA_WDOECM_Mar2025_Public_GBR_shp_2.zip")
protected_marine = parks2[parks2["MARINE"]!="0"].copy()
uk_waters = gpd.read_file("eez.zip")

unique_names = {
    'Local Nature Reserve': 'Nature Reserves',
    'Ramsar Site, Wetland of International Importance': 'Internationally Designated Sites',
    'Site of Special Scientific Interest': 'Scientific Interest Sites',
    'National Nature Reserve': 'Nature Reserves',
    'World Heritage Site (natural or mixed)': 'Internationally Designated Sites',
    'Special Protection Area': 'Internationally Designated Sites',
    'Area of Outstanding Natural Beauty': 'Landscape & Scenic Areas',
    'Area of Special Scientific Interest': 'Scientific Interest Sites',
    'Marine Protected Area (OSPAR)': 'Marine Protected Areas',
    'Marine Conservation Zone': 'Marine Protected Areas',
    'Community Marine Conservation Area': 'Marine Protected Areas',
    'Nature Conservation Marine Protected Area': 'Marine Protected Areas',
    'Nature Reserve': 'Nature Reserves',
    'Demonstration and Research Marine Protected Area': 'Marine Protected Areas',
    'UNESCO-MAB Biosphere Reserve': 'Internationally Designated Sites',
    'Emerald Network': 'Internationally Designated Sites'
}

colors = {
    'Nature Reserves': '#2ca02c',# Green
    'Scientific Interest Sites': '#1f77b4',# Blue
    'Internationally Designated Sites': '#ff7f0e',# Orange
    'Landscape & Scenic Areas': '#8c564b',# Brown
    'Marine Protected Areas': '#17becf'# Teal
}
protected_marine['DESIG_U'] = protected_marine['DESIG'].replace(unique_names)



# Protpotion *****
uk_local_authority = gpd.read_file("Local_Authority_Districts_May_2024_Boundaries_UK_BUC_3499872675230401373_1.zip")


protected_areas = parks0.drop(["LAD24NM","CTRY24NM","RGN24NM"], axis=1).to_crs(uk_local_authority.crs) #Same projecteon, same atribute

# Intersect protected areas with countries
intersected = gpd.overlay(uk_local_authority, protected_areas, how="intersection")

# Calculate«ing area
uk_local_authority["total_area_km2"] = uk_local_authority.geometry.area / (10**6)
intersected["protected_area_km2"] = intersected.geometry.area / (10**6)
# Sum protected area per local authorities
protected_sum = intersected.groupby("LAD24NM")["protected_area_km2"].sum().reset_index()
# add to local authorities
uk_local_authority = uk_local_authority.merge(protected_sum, on="LAD24NM", how="left")
uk_local_authority["protected_area_km2"] = uk_local_authority["protected_area_km2"].fillna(0)
# Calculate percentage
uk_local_authority["protected_perc"] = (uk_local_authority["protected_area_km2"] / uk_local_authority["total_area_km2"]) * 100

colors = {
    (0,20): "#006400", # Dark Green
    (21,40): "#66A032",# Olive Green
    (41,60): "#FFD700", # Yellow/Gold
    (61,80): "#FF8C00", # Orange
    (81,100): "#FF0000"  # Red
}



# Dashboar Data

#Data
uk_countries_df = gpd.read_file("Countries_December_2024_Boundaries_UK_BFC_6983126662299524946.zip")
uk_countries_df["area_km2"] = uk_countries_df.geometry.area / 1000000
uk_local_authorities_df = gpd.read_file("Local_Authority_Districts_May_2024_Boundaries_UK_BUC_3499872675230401373_1.zip")
uk_local_authorities_df["area_km2"] = uk_local_authorities_df.geometry.area / 1000000
england_regions_df = gpd.read_file("RGN_DEC_24_EN_BFC.zip")
england_regions_df["area_km2"] = england_regions_df.geometry.area / 1000000

parks_crs = parks0.to_crs(epsg=27700)

parks0["area_m2"] = parks_crs.geometry.area
parks0["area_km2"] = parks0["area_m2"]/1000000
parks0['centroid'] = parks_crs.geometry.centroid

parks0['centroid'] = parks0['centroid'].to_crs(epsg=4326)


parks0['latitude'] = parks0['centroid'].y
parks0['longitude'] = parks0['centroid'].x



# Widgets and Filters

#Selectors to Filter
countries = sorted(uk_countries_df["CTRY24NM"].unique().tolist())
countries_sl = pn.widgets.Select(name="Countries", options=countries)

england_regions = sorted(england_regions_df["RGN24NM"].unique().tolist())
england_regions_sl = pn.widgets.Select(name="England_Regions", options=england_regions)

uk_local_authorities = sorted(uk_local_authorities_df["LAD24NM"].unique().tolist())
uk_local_authorities_sl = pn.widgets.Select(name="UK_Local_Authorities", options=uk_local_authorities)

# Park Type
types_park = sorted(parks0["DESIG_U"].unique().tolist())
type_cbg = pn.widgets.CheckBoxGroup(name="Type", value=types_park, options=types_park)

# Protected ares List
protected_areas = sorted(parks0["NAME"].unique().tolist())
protected_areas_sl = pn.widgets.Select(name="Protected Areas",value="", options=protected_areas)

# Messages
message_st = pn.widgets.StaticText(name = "Message: ",value="--")

@pn.depends(countries_sl)
def get_regions(country):
    if country == "England":
        message_st.value = "--"
        england_regions_sl.disabled = False
        return [""]+sorted(england_regions_df["RGN24NM"].unique().tolist())#england_regions_df.dropna(subset = ["RGN24NM"])["RGN24NM"].unique().tolist())
    message_st.value = "Only England is divided into Regions"
    england_regions_sl.disabled = True
    return ["None"]

@pn.depends(countries_sl, england_regions_sl)
def get_local_authorities(country, region = None):
    filtered_df = uk_local_authorities_df[uk_local_authorities_df["CTRY24NM"]==country]   
    if region != "None": #**Check filter
        filtered_df = filtered_df[filtered_df["RGN24NM"] == region]
    return [""]+sorted(filtered_df["LAD24NM"].unique().tolist())

# Updating the types of park
@pn.depends(countries_sl, england_regions_sl,uk_local_authorities_sl)
def get_types_parks(country, region,lad):
    filtered_df = parks0[parks0["CTRY24NM"]==country].copy()
    if region != "None" and region != "":
        filtered_df = filtered_df[filtered_df["RGN24NM"] == region]
    if lad != "":
        filtered_df = filtered_df[filtered_df["LAD24NM"] == lad]
        
    return sorted(filtered_df["DESIG_U"].unique().tolist())

@pn.depends(countries_sl, england_regions_sl,uk_local_authorities_sl,type_cbg)
def get_protected_areas(country, region,lad, types_park):
    filtered_df = parks0[parks0["CTRY24NM"]==country].copy()
    if region != "None" and region != "":
        filtered_df = filtered_df[filtered_df["RGN24NM"] == region]
    if lad != "":
        filtered_df = filtered_df[filtered_df["LAD24NM"] == lad]   
    if len(types_park)!=0:
        filtered_df = filtered_df[filtered_df["DESIG_U"].isin(types_park)]

    return [""]+sorted(filtered_df["NAME"].unique().tolist())
    
england_regions_sl.options = get_regions
uk_local_authorities_sl.options = get_local_authorities
type_cbg.options = get_types_parks
type_cbg.value = get_types_parks
protected_areas_sl.options = get_protected_areas

location_filters = pn.Column(
    countries_sl,
    england_regions_sl,
    uk_local_authorities_sl
)




# Folium Map
def foliumMap(data, park=None):
    if not data.empty:
        c_lat = data["latitude"].mean()
        c_lon = data["longitude"].mean()
    else:
        c_lat = 53.9426
        c_lon = -2.4951

    map = folium.Map(location=[c_lat, c_lon], zoom_start=5, tiles='cartodbpositron',width='100%', height='100%',world_copy_jump=True)
    m_cluster = MarkerCluster().add_to(map)

    icons = {
        'National Park': 'tree',
        'National Nature Reserve': 'leaf',
        'UNESCO Biosphere Reserve': 'globe',
        'Heritage Coast': 'ship',
        'World Heritage Site': 'university',
        'National Scenic Area': 'binoculars',
        'Area of Outstanding Natural Beauty': 'camera',
        'Regional Park': 'map',
        'Ramsar Site': 'tint',
        'Site of Special Scientific Interest': 'flask',
        'Local Nature Reserve': 'paw'
    }

    color_map = {
        'National Park': 'green',
        'National Nature Reserve': 'darkgreen',
        'UNESCO Biosphere Reserve': 'cadetblue',
        'Heritage Coast': 'lightred',
        'World Heritage Site': 'purple',
        'National Scenic Area': 'blue',
        'Area of Outstanding Natural Beauty': 'lightgreen',
        'Regional Park': 'darkblue',
        'Ramsar Site': 'lightblue',
        'Site of Special Scientific Interest': 'orange',
        'Local Nature Reserve': 'beige'
    }

    for _, row in data.iterrows():
        desig = row.get('DESIG_U', '')
        icon_name = icons.get(desig, 'question')
        marker_color = color_map.get(desig, 'gray')

        folium.Marker(
            location=[row['latitude'], row['longitude']],
            icon=folium.Icon(icon=icon_name, prefix='fa', color=marker_color),
            popup=f"<b>{row.get('NAME', 'Unknown')}</b><br>{desig}"
        ).add_to(m_cluster)

    # Reset zomo
    map.fit_bounds(map.get_bounds(), padding=(50,30))
    
    if park:
        selected = data[data["NAME"]==park].drop("centroid",axis=1)
        #print(selected.head()) #Debugging
        seleted_json = folium.GeoJson(
            selected.to_crs(epsg=4326),  # Ensure it's in WGS84 for folium
            name=selected["NAME"],
            style={
                        'fillColor': 'green',
                        'color': "black",
                        'weight': 0.3,
                        'fillOpacity': 0.15
                        # Tool Tip and otheres ........
                    }
        )
        seleted_json.add_to(map)
        map.fit_bounds(seleted_json.get_bounds(), padding=(50,30))
        

    return map



def update_map(df,country,region, lad,types_park,park, width, height):
    data = df[df["CTRY24NM"] == country].copy()
    if region != "" and region != "None":
        data = data[data["RGN24NM"] == region]
    if lad != "":
        data = data[data["LAD24NM"] == lad]
    if len(types_park)!=0:
         data = data[data["DESIG_U"].isin(types_park)]
    #if data.empty:
        #return pn.pane.HTML("<b>No data available for the selected Local Authority</b>", width=width, height=height)
        #data=parks0.copy()
    map = foliumMap(data,park)
    return pn.pane.HTML(map._repr_html_(), 
                        #sizing_mode='stretch_both',
                        width=width, height=height,
                       )

w = 700
h = 700
main_map = pn.bind(update_map,
                   parks0,
                   countries_sl,england_regions_sl,uk_local_authorities_sl,type_cbg, protected_areas_sl,
                   w, h)




#Indicator

#Grath and data
@pn.depends(countries_sl, england_regions_sl,uk_local_authorities_sl,type_cbg)
def update_number_park_ind(country, region,lad, types_park):
    filtered_df = parks0[parks0["CTRY24NM"]==country].copy()
    if region != "None" and region != "":
        filtered_df = filtered_df[filtered_df["RGN24NM"] == region]
    if lad != "":
        filtered_df = filtered_df[filtered_df["LAD24NM"] == lad]   
    if len(types_park)!=0:
         filtered_df = filtered_df[filtered_df["DESIG_U"].isin(types_park)]
        
    number_park_ind = pn.indicators.Number(name='Total Number of Parks', value=len(filtered_df), format='{value}')
    return number_park_ind

Indicator_number = pn.WidgetBox(update_number_park_ind)





# Pie Chart
def update_chart(df,country, region,lad):
    adm = country # Country/Region/LAD
    adm_area = uk_countries_df[uk_countries_df["CTRY24NM"]==country]["area_km2"].iloc[0]
    filtered_df = df[df["CTRY24NM"]==country].to_crs(epsg=27700).copy()
    
    if region != "None" and region != "":
        filtered_df = filtered_df[filtered_df["RGN24NM"] == region]
        adm = region
        adm_area = england_regions_df[england_regions_df["RGN24NM"]==region]["area_km2"].iloc[0]
    if lad != "":
        filtered_df = filtered_df[filtered_df["LAD24NM"] == lad]
        adm = lad
        adm_area = uk_local_authorities_df[uk_local_authorities_df["LAD24NM"]==lad]["area_km2"].iloc[0]

    #filter
    filtered_df["porpotion_area"] = ((filtered_df["protected_area_km2"])/adm_area)*100
    data_plot = filtered_df.groupby("DESIG_U")["porpotion_area"].sum()
    data_plot["Non Protected Area"]=100-sum(data_plot.values)
    data_plot = data_plot.reset_index(name='Percentage').rename(columns={'DESIG_U':'Protected_area_type'})
    data_plot["angle"] = data_plot["Percentage"]/data_plot["Percentage"].sum()*2*pi
    # Assigning colors
    if len(data_plot) in Category20c:
        colors = Category20c[len(data_plot)]
    else:
        colors = Category20c[3][:len(data_plot)]  # Pick 3 colors and slice

    data_plot["color"] = colors

    data_plot['legend_label'] = data_plot['Protected_area_type'] + ": " + round(data_plot['Percentage'],2).astype(str)+"%"

    p = figure(height=300, title = adm+" Percenge occupied by", toolbar_location=None, width=550,
               tools="hover", tooltips="@Protected_area_type: @Percentage", x_range=(-0.3,1.0))

    r = p.wedge(x=0, y=1, radius=0.25,
                start_angle=cumsum("angle",include_zero=True), end_angle=cumsum("angle"),
                line_color="white", fill_color="color", legend_field="legend_label", source=data_plot)

    p.axis.visible=False
    p.grid.grid_line_color = None 
    p.legend.location = "right"#"top_right"
    #p.add_layout(p.legend[0], 'right')
    bokeh_pane = pn.pane.Bokeh(p, theme="dark minimal")

    return bokeh_pane
    

pie_chart = pn.bind(update_chart,
                   intersected, ### Overlaydess
                   countries_sl,england_regions_sl,uk_local_authorities_sl,
                   )


# Informations

@pn.depends(protected_areas_sl)
def update_info_park(park_name):
    # See if park is empty
    if park_name is None or park_name == "":

        styles = {
            #'background-color': '#F6F6F6', #'border': '2px solid black',
            'border-radius': '5px', 'padding': '10px',
            "padding": "20px",
            }
        
        html_content = """
        <h3>No Park Selected</h3>
        <p>Please select a park to view information.</p>
        """
        
        return pn.pane.HTML(html_content, styles=styles,)
    
    
    park = parks0[parks0["NAME"] == park_name].iloc[0]
    
    
    styles = {
    #'background-color': '#F6F6F6', #'border': '1px solid black',
    'border-radius': '5px', 'padding': '10px'
    }
    
    
    # Create the HTML content
    html_content = f"""
    <h2>{park['NAME']}</h2>
    <p><strong>Designation (Type):</strong> {park['DESIG_U']}</p>
    <p><strong>IUCN Category:</strong> {park['IUCN_CAT']}</p>
    <p><strong>Total Area (Km²):</strong> {park['area_km2']:.2f}</p>
    <p><strong>Status:</strong> {park['STATUS']}</p>
    <p><strong>Location:</strong></p>
    <ul>
        <li><strong>Country:</strong> {park['CTRY24NM']}</li>
        <li><strong>Administrative Authority:</strong> {park['LAD24NM']}</li>
        <li><strong>Latitude:</strong> {park['latitude']:.4f}</li>
        <li><strong>Longitude:</strong> {park['longitude']:.4f}</li>
    </ul>
    <p><a href="https://www.protectedplanet.net/" target="_blank" style="color: #1e90ff;">More Information</a></p>
    """
    
    html_pane = pn.pane.HTML(html_content, styles=styles,sizing_mode="stretch_both")
    
    return html_pane

Informacoes=pn.WidgetBox(update_info_park)
"""
Informacoes=pn.Column(update_info_park, height=500, width=270,
                     )
"""



#
# Search a foto of the park on internet
def search_images(keywords, max_images=200):
    results = DDGS().images(keywords, max_results=max_images)
    urls = []
    for r in results:
        url = r['image']
        if '.jpeg' in url:
            url = url.split('.jpeg')[0]+'.jpeg'
        elif '.jpg' in url:
            url = url.split('.jpg')[0] +'.jpg'
        elif '.png' in url:
            url = url.split('.png')[0]+ '.png'
        urls.append(url)
    return urls

@pn.depends(protected_areas_sl)
def update_image(park_name):
    if park_name is None or park_name == "":
        #return pn.pane.Image(" https://sci-techdaresbury.com/wp-content/uploads/2023/03/University-of-Liverpool-TN.jpg").clone(width=300)
        return pn.pane.Image("https://upload.wikimedia.org/wikipedia/commons/6/65/No-Image-Placeholder.svg", #width=275, height=250,
                        sizing_mode='stretch_both',
                        #embed=False,
                              #sizing_mode='scale_both',
                        alt_text="Image",
                            )
    else:
        urls = search_images('Uk protected area+'+park_name, max_images=1)
        return pn.pane.Image(urls[0], #width=275, height=250,
                        sizing_mode='stretch_both',
                        #embed=False,
                              #sizing_mode='scale_both',
                        alt_text="Image",
                            )

Image_p = pn.WidgetBox(update_image)
"""
Image=pn.Column(update_image,
    update_image,
    height=250, width=270, styles={'background': '#f0f0f0'})
"""




# Final Layout
countries_sl.width = 250
england_regions_sl.width = 250
uk_local_authorities_sl.width = 250
#location_filters.width = 250
type_cbg.width =250
protected_areas_sl.width = 250


Filters = pn.WidgetBox(
    '# Filters:',
    location_filters,
    type_cbg,
    protected_areas_sl,
    #sizing_mode='stretch_both',  # or 'stretch_width' or 'fixed'
    #max_width=250                # adjust as needed
)


#GRid
gspec = pn.GridSpec(width=1100, height=700, nrows=5, ncols=4)

gspec[0:3, 0] = Filters  # Filters (still 2 rows)
gspec[3:5, 0] = Indicator_number  # Indicator (still 1 row)
#gspec2[0:3, 1:3] = pn.WidgetBox(pn.Column(main_map))  # Main Map (3 rows)
gspec[0:3, 1:3] =pn.WidgetBox( pn.Column(main_map,#height=400,width=600, sizing_mode=None,
                        styles={'overflow': 'auto', 'border': '1px solid lightgray'})) # Main Map (3 rows)
gspec[3:5, 1:3] = pn.WidgetBox(pie_chart)  # Pie Chart (2 rows)
gspec[0:1, 3] = Image_p  # Photo
gspec[1:5, 3] = Informacoes  # Info (adjusted to take more vertical space)

protected_marine = parks2[parks2["MARINE"]!="0"].copy()

unique_names = {
    'Local Nature Reserve': 'Nature Reserves',
    'Ramsar Site, Wetland of International Importance': 'Internationally Designated Sites',
    'Site of Special Scientific Interest': 'Scientific Interest Sites',
    'National Nature Reserve': 'Nature Reserves',
    'World Heritage Site (natural or mixed)': 'Internationally Designated Sites',
    'Special Protection Area': 'Internationally Designated Sites',
    'Area of Outstanding Natural Beauty': 'Landscape & Scenic Areas',
    'Area of Special Scientific Interest': 'Scientific Interest Sites',
    'Marine Protected Area (OSPAR)': 'Marine Protected Areas',
    'Marine Conservation Zone': 'Marine Protected Areas',
    'Community Marine Conservation Area': 'Marine Protected Areas',
    'Nature Conservation Marine Protected Area': 'Marine Protected Areas',
    'Nature Reserve': 'Nature Reserves',
    'Demonstration and Research Marine Protected Area': 'Marine Protected Areas',
    'UNESCO-MAB Biosphere Reserve': 'Internationally Designated Sites',
    'Emerald Network': 'Internationally Designated Sites'
}

colors = {
    'Nature Reserves': '#2ca02c',                 # Green
    'Scientific Interest Sites': '#1f77b4',       # Blue
    'Internationally Designated Sites': '#ff7f0e',# Orange
    'Landscape & Scenic Areas': '#8c564b',        # Brown
    'Marine Protected Areas': '#17becf'           # Teal
}

protected_marine['DESIG_U'] = protected_marine['DESIG'].replace(unique_names)

#uk_waters = gpd.read_file("eez.zip")



##

protected_marine['geometry'] = protected_marine.geometry.simplify(tolerance=0.001, preserve_topology=True)
protected_marine = protected_marine.to_crs(epsg=27700)


#parks_crs = parks0.to_crs(epsg=27700)
#*** Double check
protected_marine["area_m2"] = protected_marine.geometry.area
protected_marine['latitude'] = protected_marine.geometry.centroid.to_crs(epsg=4326).y
protected_marine['longitude'] = protected_marine.geometry.centroid.to_crs(epsg=4326).x



import folium

# 2. Create folium map centered on the UK
map_center = [protected_marine.geometry.centroid.to_crs(epsg=4326).y.mean(), protected_marine.geometry.centroid.to_crs(epsg=4326).x.mean()]

map_mar = folium.Map(location=map_center, zoom_start=5, tiles='cartodbpositron',world_copy_jump=True,width='100%', height='100%')

# 3. Add protected areas by category, with color styling
for site, color in colors.items():
    site_gdf = protected_marine[protected_marine["DESIG_U"] == site]
    
    if not site_gdf.empty:
        folium.GeoJson(
            site_gdf.to_crs(epsg=4326),
            name=site,
            style_function=lambda feature, col=color: {
                'fillColor': col,
                'color': col,
                'weight': 1,
                'fillOpacity': 0.5
            },
            tooltip=folium.GeoJsonTooltip(fields=['NAME'], aliases=['NAME:'])
        ).add_to(map_mar)


#uk_waters

#print(selected.head()) #Debugging
uk_waters_json = folium.GeoJson(
    uk_waters.to_crs(epsg=4326),
    name='UK EEZ',
    style_function=lambda x: {
        'fillColor': 'none',
        'color': 'darkblue',       # Outline color
        'weight': 0.3,
        'fillOpacity': 0.15,
        'dashArray': '5,5'         # Dashed outline, Leaflet style
    }
)
uk_waters_json.add_to(map_mar)


def findPark_water(park,width, height):
    
    if park:
       selected = protected_marine[protected_marine["NAME"]==park]
       #print(selected.head()) #Debugging
       seleted_json = folium.GeoJson(
           selected.to_crs(epsg=4326),
           name=selected["NAME"],
       )
       
       map_mar.fit_bounds(seleted_json.get_bounds(), padding=(50, 50))
    
    return pn.pane.HTML(map_mar._repr_html_(),
                        width=width, height=height,
                        #sizing_mode='stretch_height'
                       )


autocomplete = pn.widgets.AutocompleteInput(
    name='Input the park', options=protected_marine["NAME"].tolist(),
    case_sensitive=False, search_strategy='includes',
    placeholder='Write the park',
    sizing_mode='stretch_width'

)



w = 1150
h = 1150
main_map_water = pn.bind(findPark_water,
                   autocomplete,
                   w, h
                  )



@pn.depends(autocomplete)
def update_info_park_water(park_name):
    # See if park is empty
    if park_name is None or park_name == "":
        styles = {
            "font-family": "Arial, sans-serif",
            "padding": "20px",
            "background-color": "#fff3cd",
            "border-radius": "10px",
            "box-shadow": "0 4px 8px rgba(0,0,0,0.1)",
            "line-height": "1.6",
            "color": "#856404",
            "text-align": "center",
        }
        
        html_content = """
        <h3>No Park Selected</h3>
        <p>Please select a park to view its information.</p>
        """
        
        return pn.pane.HTML(html_content, styles=styles,)
    
    
    park = protected_marine[protected_marine["NAME"] == park_name].iloc[0]
    
    """
    styles = {
        "font-family": "Arial, sans-serif",
        "padding": "20px",
        "background-color": "#f9f9f9",
        "border-radius": "10px",
        "box-shadow": "0 4px 8px rgba(0,0,0,0.1)",
        "line-height": "1.6",
        "color": "#333",
    }
    
    """
    
    styles = {
    'background-color': '#F6F6F6', 'border': '2px solid black',
    'border-radius': '5px', 'padding': '10px'
    }

    
    # Create the HTML content
    html_content = f"""
    <h2>{park['NAME']}</h2>
    <p><strong>Designation (Type):</strong> {park['DESIG_U']}</p>
    <p><strong>IUCN Category:</strong> {park['IUCN_CAT']}</p>
    <p><strong>Total Area (m²):</strong> {park['area_m2']:.2f}</p>
    <p><strong>Status:</strong> {park['STATUS']}</p>
    <p><strong>Location:</strong></p>
    <ul>
        <li><strong>Latitude:</strong> {park['latitude']:.4f}</li>
        <li><strong>Longitude:</strong> {park['longitude']:.4f}</li>
    </ul>
    <p><a href="https://www.protectedplanet.net/" target="_blank" style="color: #1e90ff;">More Information</a></p>
    """
    
    html_pane = pn.pane.HTML(html_content, styles=styles,sizing_mode="stretch_both")
    
    return html_pane



Informacoes_water=pn.WidgetBox(update_info_park_water)


gspec_water = pn.GridSpec(width=1100, height=700, nrows=5, ncols=4)

gspec_water[0,0] = pn.WidgetBox('# Search Park:',autocomplete)
gspec_water[1:5, 0] = Informacoes_water
gspec_water[0:5, 1:4] =pn.WidgetBox( pn.Column(main_map_water,#height=400,width=600, sizing_mode=None,
                        styles={'overflow': 'auto', 'border': '1px solid lightgray'})) 


# Help page

help_page = pn.pane.HTML("""
<div style="padding: 20px; max-width: 950px; font-family: Arial, sans-serif;">
    <h1>UK Protected Areas Dashboard</h1>
    <p>This dashboard allows you to explore various types of protected natural areas across the United Kingdom using interactive filters and visualizations.</p>

    <h2>Filters and Selectors</h2>
    <ul>
        <li><strong>Countries:</strong> Select a UK country to begin filtering (e.g., England, Scotland).</li>
        <li><strong>England Regions:</strong> Becomes available if "England" is selected, for filtering by region.</li>
        <li><strong>Local Authorities:</strong> Further refine the selection by administrative area.</li>
        <li><strong>Type:</strong> Choose one or more types of protected areas.</li>
        <li><strong>Protected Areas:</strong> Select a specific site to view its detailed information and highlight it on the map.</li>
    </ul>

    <h2>Map Behavior</h2>
    <p>The central map displays protected areas with color-coded icons based on their designation. The map centers on selected filters and zooms into specific parks when chosen.</p>

    <h3>Map Legend</h3>
    <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
        <thead>
            <tr style="background-color: #f2f2f2;">
                <th style="border: 1px solid #ddd; padding: 8px;">Designation</th>
                <th style="border: 1px solid #ddd; padding: 8px;">Icon</th>
                <th style="border: 1px solid #ddd; padding: 8px;">Color</th>
            </tr>
        </thead>
        <tbody>
            <tr><td style="border: 1px solid #ddd; padding: 8px;">National Park</td><td style="border: 1px solid #ddd; padding: 8px;">tree</td><td style="border: 1px solid #ddd; padding: 8px;">green</td></tr>
            <tr><td style="border: 1px solid #ddd; padding: 8px;">National Nature Reserve</td><td style="border: 1px solid #ddd; padding: 8px;">leaf</td><td style="border: 1px solid #ddd; padding: 8px;">darkgreen</td></tr>
            <tr><td style="border: 1px solid #ddd; padding: 8px;">UNESCO Biosphere Reserve</td><td style="border: 1px solid #ddd; padding: 8px;">globe</td><td style="border: 1px solid #ddd; padding: 8px;">cadetblue</td></tr>
            <tr><td style="border: 1px solid #ddd; padding: 8px;">Heritage Coast</td><td style="border: 1px solid #ddd; padding: 8px;">ship</td><td style="border: 1px solid #ddd; padding: 8px;">lightred</td></tr>
            <tr><td style="border: 1px solid #ddd; padding: 8px;">World Heritage Site</td><td style="border: 1px solid #ddd; padding: 8px;">university</td><td style="border: 1px solid #ddd; padding: 8px;">purple</td></tr>
            <tr><td style="border: 1px solid #ddd; padding: 8px;">National Scenic Area</td><td style="border: 1px solid #ddd; padding: 8px;">binoculars</td><td style="border: 1px solid #ddd; padding: 8px;">blue</td></tr>
            <tr><td style="border: 1px solid #ddd; padding: 8px;">Area of Outstanding Natural Beauty</td><td style="border: 1px solid #ddd; padding: 8px;">camera</td><td style="border: 1px solid #ddd; padding: 8px;">lightgreen</td></tr>
            <tr><td style="border: 1px solid #ddd; padding: 8px;">Regional Park</td><td style="border: 1px solid #ddd; padding: 8px;">map</td><td style="border: 1px solid #ddd; padding: 8px;">darkblue</td></tr>
            <tr><td style="border: 1px solid #ddd; padding: 8px;">Ramsar Site</td><td style="border: 1px solid #ddd; padding: 8px;">tint</td><td style="border: 1px solid #ddd; padding: 8px;">lightblue</td></tr>
            <tr><td style="border: 1px solid #ddd; padding: 8px;">Site of Special Scientific Interest</td><td style="border: 1px solid #ddd; padding: 8px;">flask</td><td style="border: 1px solid #ddd; padding: 8px;">orange</td></tr>
            <tr><td style="border: 1px solid #ddd; padding: 8px;">Local Nature Reserve</td><td style="border: 1px solid #ddd; padding: 8px;">paw</td><td style="border: 1px solid #ddd; padding: 8px;">beige</td></tr>
        </tbody>
    </table>

    <h2>Indicators and Charts</h2>
    <p>Displays a count of matching parks and a pie chart showing their proportional coverage in the selected area.</p>

    <h2>Park Details Panel</h2>
    <p>When a park is selected, detailed information and an image (if available) are shown on the right panel.</p>

    <h2>Notes</h2>
    <ul>
        <li>Only England is subdivided into regions.</li>
        <li>All widgets are interconnected — selections update each other dynamically.</li>
        <li>The map zooms to the selected area or park automatically.</li>
    </ul>

    <p style="color: #666; font-size: 90%;">Data sourced from UK government geospatial datasets.</p>

    <hr style="margin: 30px 0;">
    <h2>Marine Protected Areas Tab</h2>
    <p>This tab provides an interactive view of designated marine and coastal protected areas within UK territorial waters.</p>
    
    <h3>How It Works</h3>
    <ul>
      <li><strong>Search Park:</strong> Use the autocomplete box to search for a specific marine site by name.</li>
      <li><strong>Interactive Map:</strong> The map displays various categories of marine protection, each shaded with a distinct color. Hover over areas to see their names, and click to zoom in.</li>
      <li><strong>Designations:</strong> Marine parks are grouped under broader categories based on their designation:</li>
    </ul>
    
    <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
      <thead>
        <tr style="background-color: #f2f2f2;">
          <th style="border: 1px solid #ddd; padding: 8px;">Designation Category</th>
          <th style="border: 1px solid #ddd; padding: 8px;">Color</th>
        </tr>
      </thead>
      <tbody>
        <tr><td style="border: 1px solid #ddd; padding: 8px;">Nature Reserves</td><td style="border: 1px solid #ddd; padding: 8px; background-color: #2ca02c;">#2ca02c</td></tr>
        <tr><td style="border: 1px solid #ddd; padding: 8px;">Scientific Interest Sites</td><td style="border: 1px solid #ddd; padding: 8px; background-color: #1f77b4;">#1f77b4</td></tr>
        <tr><td style="border: 1px solid #ddd; padding: 8px;">Internationally Designated Sites</td><td style="border: 1px solid #ddd; padding: 8px; background-color: #ff7f0e;">#ff7f0e</td></tr>
        <tr><td style="border: 1px solid #ddd; padding: 8px;">Landscape & Scenic Areas</td><td style="border: 1px solid #ddd; padding: 8px; background-color: #8c564b;">#8c564b</td></tr>
        <tr><td style="border: 1px solid #ddd; padding: 8px;">Marine Protected Areas</td><td style="border: 1px solid #ddd; padding: 8px; background-color: #17becf;">#17becf</td></tr>
      </tbody>
    </table>
    
    <h3>Marine Boundaries</h3>
    <p>The blue dashed outline on the map represents the UK's Exclusive Economic Zone (EEZ). Protected sites are displayed only if they fall within marine zones (not purely terrestrial).</p>
    
    <h3>Park Info Panel</h3>
    <p>Upon selecting a marine park, detailed information is shown on the left, including designation, area, IUCN category, and geographic coordinates. A link to Protected Planet is also provided for further details.</p>
</div>
""", sizing_mode='stretch_width')

gspec_help = pn.GridSpec(width=1100, height=700, nrows=5, ncols=4) # to match the size of others dahsvoard
gspec_help[0:5,0:4] = pn.WidgetBox( pn.Column(help_page,#height=400,width=600, sizing_mode=None,
                        styles={'overflow': 'auto', 'border': '1px solid lightgray'})) 


dashboard = pn.Tabs(("Land Protected Areas", gspec),("Marine Protected Areas", gspec_water),("Help", gspec_help))


title = 'Atanilson Assignment'

dashboard.servable(title=title)