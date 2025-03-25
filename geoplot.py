import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx


# Parameter format: kmeans_output = [(Cluster ID, [Longitude, Latitude]), (), (), ...]
def geoplot(kmeans_output):
    
    # Convert to a DataFrame
    data = pd.DataFrame(kmeans_output, columns=["classification", "coordinates"])

    # Split the coordinates into longitude and latitude columns
    data["longitude"] = data["coordinates"].apply(lambda x: x[0])
    data["latitude"] = data["coordinates"].apply(lambda x: x[1])

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(
        data,
        geometry=gpd.points_from_xy(data.longitude, data.latitude),
        crs="EPSG:4326"  # WGS84 coordinate system
    )

    # Reproject to Web Mercator for compatibility with basemaps
    gdf = gdf.to_crs("EPSG:3857")

    # Plotting
    fig, ax = plt.subplots(figsize=(5, 5))

    # Plot points with classification colors
    for cluster in gdf["classification"].unique():
        cluster_gdf = gdf[gdf["classification"] == cluster]
        cluster_gdf.plot(ax=ax, markersize=10, label=f"Cluster {cluster}")

    # Add basemap
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

    ax.set_title("K-means Clustering on Baltimore Crime Data")
    ax.legend()
    plt.show()
