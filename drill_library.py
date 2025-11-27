import streamlit as st
import pandas as pd
import numpy as np
from drill_plots import drills_comp_radar_chart

def drills_page(drill_data=None,
                drill_data_players=None):
    

    rename_columns = {'total_time_min':'Exposure (min)',
                  'total_distance':'Total Distance (m)',
                  'total_distance_min':'Dist per minute (m/min)',
                  'Accelerations  (Absolute)':'Acc. >3 m/s² (n)',
                  'Accelerations  (Absolute)_min':'Acc. >3 m/s² (n/min)',
                  'Accelerations Zone 5 - Zone 6 (Absolute)_min':'Acc. >4 m/s² (n/min)',
                  'Accelerations Zone 5 - Zone 6 (Absolute)':'Acc. >4 m/s² (n)',
                  'Decelerations (Absolute)':'Decel. >3 m/s² (n)',
                  'Decelerations (Absolute)_min':'Decel. >3 m/s² (n/min)',
                  'HP Distance_min':'Distance >20 W/kg (m/min)',
                  'HP Distance':'Distance >20 W/kg (m)',
                  'HML Distance_min':'Distance >25 W/kg (m/min)',
                  'HML Distance':'Distance >25 W/kg (m)',
                  'VHP Distance_min':'Distance >35 W/kg (m/min)',
                  'VHP Distance':'Distance >35 W/kg (m)',
                  'High Speed Running (Absolute)_min':'Distance >19.8 km/h (m/min)',
                  'High Speed Running (Absolute)':'Distance >19.8 km/h (m)',
                  'Distance Zone 6 (Absolute)_min':'Distance >25.2 km/h (m/min)',
                  'Distance Zone 6 (Absolute)':'Distance >25.2 km/h (m)'}

    # --- CSS per centrare le tabs ---
    st.markdown("""
        <style>
        /* Centra il container delle tab */
        div[data-baseweb="tab-list"] {
            justify-content: center !important;
        }

        /* (opzionale) Migliora estetica */
        div[data-baseweb="tab"] {
            font-size: 16px !important;
            font-weight: 500 !important;
            color: #333 !important;
            padding: 6px 20px !important;
            border-radius: 6px 6px 0 0 !important;
        }

        div[data-baseweb="tab"][aria-selected="true"] {
            border-bottom: 3px solid #4A90E2 !important;
            color: #000 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if drill_data is not None:

        lst_teams = ['first team', 'reserve n3', 'pro2', 'u19', 'u17', 'u15 prefo', 'u14 prefo']#[x for x in list(drill_data.keys()) if str(x)!="none"]
        select_team = st.selectbox("Select team",lst_teams)

        lst_players = ['TEAM']+sorted([x for x in list(drill_data_players[select_team].keys()) if 'test' not in x.lower()])
        select_player = st.selectbox("Select player",lst_players)

        if select_player == 'TEAM':
            drill_data_ = drill_data[select_team]
            lst_drills_all = sorted(list(drill_data_.keys()))
        else:
            drill_data_ = drill_data_players[select_team][select_player]
            lst_drills_all = sorted(list(drill_data_.keys()))

        def drill_comparator():

            multiselect_drill = st.multiselect("Select drills to compare", lst_drills_all)

            if len(multiselect_drill)>0:
                val_sel = pd.DataFrame()
                for d in multiselect_drill:
                    val_sel = pd.concat([val_sel,pd.DataFrame(drill_data_[d],index=[d])])

                rel_val = val_sel[[x for x in list(val_sel) if '_min' in x]]
                abs_val = val_sel[[x for x in list(val_sel) if '_min' not in x]]
                rel_val.columns = [rename_columns.get(x,x) for x in rel_val.columns]

                del rel_val['Exposure (min)']
                abs_val.columns = [rename_columns.get(x,x) for x in abs_val.columns]

                figAbs,figRel,_df_ = drills_comp_radar_chart(drill_data_,multiselect_drill,rename_columns)

                col1, col2 = st.columns(2)
                with col1:
                    st.pyplot(figAbs)
                with col2:
                    st.pyplot(figRel)
                
                with st.expander("Show relative values details"):
                    st.markdown(f"<h2 style='text-align: center;color:black '> Valori relativi (per minuto) </h2>", unsafe_allow_html=True)
                    st.table(rel_val.T.style.format('{:.0f}', na_rep=" ")\
                                    .apply(lambda x: ['font-weight: bold' 
                                            if (x.name == 'Valori per ora')
                                            else '' for i in x], axis=1)\
                                    .set_properties(**{'text-align': 'center'})\
                                    .set_table_styles([dict(selector='th', props=[('text-align', 'center')])]))
                
                with st.expander("Show absolute values details"):

                    st.markdown(f"<h2 style='text-align: center;color:black '> Valori assoluti </h2>", unsafe_allow_html=True)
                    st.table(abs_val.T.style.format('{:.0f}', na_rep=" ")\
                                    .apply(lambda x: ['font-weight: bold' 
                                            if (x.name == 'Valori per ora')
                                            else '' for i in x], axis=1)\
                                    .set_properties(**{'text-align': 'center'})\
                                    .set_table_styles([dict(selector='th', props=[('text-align', 'center')])]))
                    

        def training_creator():
        
            if 'n_drill' not in st.session_state:
                st.session_state['n_drill'] = 1

            if 'drill_1' not in st.session_state:
                st.session_state['drill_1'] = ' '

            if 'time__1' not in st.session_state:
                st.session_state['time_1'] = 1

            def clear_multi():
                st.session_state['n_drill'] = 1
                st.session_state['drill_1'] = ' '
                st.session_state['time_1'] = " "
                st.session_state[" "] = " "
                st.session_state["1"] = 1
                return

            st.markdown(f"<h2 style='text-align: center;color:black '> Build your training </h2>", unsafe_allow_html=True)
            st.session_state['n_drill'] = st.number_input("Select the total numeber of drills",min_value=1,max_value=10,value=st.session_state['n_drill'])

            st.markdown("""<hr style="height:2px;border:none;color:white;background-color:black;" /> """,
                        unsafe_allow_html=True)

            lst_drills = []
            for i in range(1,st.session_state.n_drill+1):

                if i == 1:
                    if st.session_state['drill_1'] == ' ':
                        c1, c2 = st.columns((4,2))
                        with c1:
                            drill_sel = st.selectbox("Select the drill %i"%i,[' ']+lst_drills_all,key=st.session_state['drill_1'])
                        with c2:
                            time_drill = st.number_input('Drill %i duration'%i,min_value=1,value=1,key=st.session_state['time_1'])
                    else:
                        c1, c2 = st.columns((4,2))
                        with c1:
                            drill_sel = st.selectbox("Select the drill %i"%i,[' ']+lst_drills_all)
                        with c2:
                            time_drill = st.number_input('Drill %i duration'%i,min_value=1)
                        st.session_state['drill_1'] = drill_sel
                        st.session_state['time_1'] = time_drill
                else:
                    c1, c2 = st.columns((4,2))
                    with c1:
                        drill_sel = st.selectbox("Select the drill %i"%i,[' ']+lst_drills_all)
                    with c2:
                        time_drill = st.number_input('Drill %i duration'%i,min_value=1)


                if drill_sel != ' ':
                    val_sel = pd.DataFrame(drill_data_[drill_sel],index=[drill_sel])
                    val_rel = val_sel[[x for x in list(val_sel) if '_min' in x]]*time_drill
                    val_rel['duration'] = time_drill

                    val_drill = ['duration']
                    for col in val_rel:
                        val_drill.append(col.split('_')[0])

                    lst_drills.append(val_rel)

                st.markdown("""<hr style="height:1px;border:none;color:white;background-color:black;" /> """,
                        unsafe_allow_html=True)

            try:  
                st.markdown(f"<h3 style='text-align: center;color:black '> Simulated training resume </h3>", unsafe_allow_html=True)
                df_drills = pd.concat(lst_drills).T
                df_drills[' '] = [np.nan]*len(df_drills)
                df_drills['TOTAL'] = df_drills.sum(axis=1)
                df_drills = round(df_drills,0)
                df_drills.index = [x.split('_min')[0] if x != 'duration' else 'Duration (min)' for x in df_drills.index]
                lst_index = [x for x in df_drills.index if x != 'total_time' and x != 'Time In Heart Rate Zone 4 - Zone 6 (Relative)' and 'Tempo' not in x]
                df_drills = df_drills.loc[['Duration (min)'] + lst_index[:-1]]
                df_drills = df_drills.rename(index=rename_columns)
                st.table(df_drills.T.style.format('{:.0f}', na_rep=" ")\
                                .apply(lambda x: ['font-weight: bold' 
                                        if (x.name == 'TOTAL')
                                        else '' for i in x], axis=1)\
                                .set_properties(**{'text-align': 'center'})\
                                .set_table_styles([dict(selector='th', props=[('text-align', 'center')])]))
                
                st.info("Note: the values refers only to effective drills values without breaks. In general the total training time will be ~20\% higher considering rest time between drills.", icon="ℹ️")
            except:
                pass

            st.markdown("""<hr style="height:2px;border:none;color:white;background-color:black;" /> """,
                        unsafe_allow_html=True)

            st.button("RESET", on_click=clear_multi)

        tab1, tab2 = st.tabs(["Drill comparator", "Training creator"])

        if tab1:
            with tab1:
                drill_comparator()
        if tab2:
            with tab2:
                training_creator()