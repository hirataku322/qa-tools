import os
from pathlib import Path

import matplotlib.pyplot  as plt
import matplotlib.patches as patches

import dwave_networkx as dnx
from dwave.system import DWaveSampler

plt.rcParams["savefig.bbox"]       = "tight"
plt.rcParams["savefig.pad_inches"] = 0

def plot_working_graph(sampler: DWaveSampler, out_path: None or os.PathLike=None, 
                       figsize:tuple=(8, 8), ng_color:str="red", ok_color:str="blue",
                       draw_rectangle:bool=False) -> None:
    """
    QPUのworking graphをプロットする。

    working graph については https://docs.dwavesys.com/docs/latest/c_gs_4.html?highlight=working%20graph を参考。

    Parameters
    ----------
    sampler : DWaveSampler
        プロット対象のQPUを保持するDWaveSamplerオブジェクト。
    out_path : None or os.PathLike, optional
        出力パス, by default None
    figsize : tuple, optional
        figsize, by default (8, 8)
    ng_color : str, optional
        無効なqbit, couplerの描画色, by default "red"
    ok_color : str, optional
        有効なqbit, couplerの描画色, by default "blue"
    draw_rectangle : bool, optional
        無効なqbit, couplerが存在しない領域を示すか, by default False
        DWaveSampler.properties["chip_id"] が "DW_2000Q_6" である時のみ使える。
        それ以外のSamplerに対しTrueを設定するとValueErrorが発生する。
        矩形のサイズは手動で調整した。ハードコーディング。
    """

    # topologyに応じ関数を設定
    topology_type = sampler.properties["topology"]["type"]
    if topology_type == "chimera":
        graph_func = dnx.chimera_graph
        draw_func  = dnx.draw_chimera
    elif topology_type == "pegasus":
        graph_func = dnx.pegasus_graph
        draw_func  = dnx.draw_pegasus
    else:
        raise ValueError(f"support chimera or pegasus, unsupported {topology_type}.")
    
    # working_graph の 無効なqbit, coupler を求め、colorリストを作成
    G = sampler.to_networkx_graph()
    T = graph_func(*sampler.properties["topology"]["shape"])

    error_node = set(T.nodes() - G.nodes())
    node_color = [ng_color if v in error_node else ok_color for v in T.nodes()]

    error_edge = set(T.edges() - G.edges())
    edge_color = [ng_color if e in error_edge else ok_color for e in T.edges()]
    
    # プロット
    plt.figure(figsize=figsize)
    ax  = plt.axes()
    draw_func(T, node_color=node_color, edge_color=edge_color, node_size=1, ax=ax)

    if draw_rectangle:
        chip_id = sampler.properties["chip_id"]
        if chip_id != "DW_2000Q_6":
            raise ValueError(f"support DW_2000Q_6, unsupported {chip_id}.")
        # ハードコーディング。手動で調整した。
        rectangle = patches.Rectangle(xy=(0.37, -0.82), width=0.64, height=0.83, 
                                      ec='green', fill=False, ls="--", lw="2")
        ax.add_patch(rectangle)

    if out_path is None:
        plt.show()
    else:
        os.makedirs(Path(out_path).parent, exist_ok=True)
        plt.savefig(out_path)
    
    plt.clf()