#!/bin/bash
echo "####################################################################################"
echo "RUNNING EIGHTEEN FACILITIES EXPERIMENT"
echo "####################################################################################"
echo -e "\n"

###############################

# VARIABLES
output_dir=experiments/eighteen_facilities
config_path="${output_dir}/config.ini"
file_path="${output_dir}/results.csv"

tabu_sizes=(5 7 15)
T_values=(50 200 300)
Tf_values=(1 20 50)
alpha_values=(0.9 0.95 0.99)
neighbors_percentages=(0.25 0.5 0.75)
# change it based on N=facilities_count*4
# it should be set(max(10,0.15*N) max(10,0.3*N) max(10,0.5*N))
K_values=(10 20 36)

###############################

echo "####################################################################################"
echo "SETUP EXPERIMENT ENVIRONMENT"
echo "####################################################################################"
echo -e "\n"

# create csv results file and add the headers
echo \
"solution index",\
"tabu size",\
"T",\
"Tf",\
"alpha",\
"K",\
"neighbors size",\
"neighbors percentage",\
"greedy Z1",\
"hybrid Z1",\
"normalized hybrid Z1",\
"greedy Z2",\
"hybrid Z2",\
"normalized hybrid Z2",\
"greedy Z3",\
"hybrid Z3",\
"normalized hybrid Z3",\
"greedy multi objective value",\
"hybrid multi objective value",\
"normalized hybrid multi objective value",\
"w1","w2","w3",\
"weighted multi objective value",\
"optimization running time",\
"open/close status of facilities" > $file_path

# create the tmp_solutions directory 
mkdir -p "${output_dir}/tmp_solutions"

###############################

echo "####################################################################################"
echo "EXECUTE EXPERIMENT"
echo "####################################################################################"
echo -e "\n"

for tabu_size in ${tabu_sizes[@]}
do
  for T in ${T_values[@]}
  do
    for Tf in ${Tf_values[@]}
    do
      for alpha in ${alpha_values[@]}
      do
        for K in ${K_values[@]}
        do
          for neighbors_percentage in ${neighbors_percentages[@]}
          do
            python scripts/run_hybrid_algorithm_optimizer.py\
              --config_path $config_path\
              --tabu_size $tabu_size\
              -T $T\
              -Tf $Tf\
              --alpha $alpha\
              -K $K\
              --neighbors_percentage $neighbors_percentage >> "${output_dir}/tmp_solutions/${tabu_size}_${K}_${T}_${Tf}_${alpha}_${neighbors_percentage}.sol" &&\
            echo "####################################################################################" &&\
            echo Done with Tabu Size=$tabu_size, T=$T, Tf=$Tf, alpha=$alpha K=${K} Neighbors Percentage = $neighbors_percentage &&\
            echo "####################################################################################"&
          done
        done
      done
    done
  done
  wait
done

###############################

echo -e "\n"
echo "####################################################################################"
echo "COLLECT RESULTS"
echo "####################################################################################"
echo -e "\n"

for tabu_size in ${tabu_sizes[@]}
do
  for T in ${T_values[@]}
  do
    for Tf in ${Tf_values[@]}
    do
      for alpha in ${alpha_values[@]} 
      do
        for K in ${K_values[@]}
        do
          for neighbors_percentage in ${neighbors_percentages[@]}
          do
            cat "${output_dir}/tmp_solutions/${tabu_size}_${K}_${T}_${Tf}_${alpha}_${neighbors_percentage}.sol" >> $file_path
          done
        done
      done
    done
  done
done

###############################

echo "####################################################################################"
echo "CLEAN AND FINALIZE"
echo "####################################################################################"
echo -e "\n"

rm -r "${output_dir}/tmp_solutions"

###############################

echo "####################################################################################"
echo "THREE FACILITIES EXPERIMENT COMPLETED"
echo "####################################################################################"
echo -e "\n"

###############################