
#Author:Ali Vala BARBAROS
#June 8,2013 
#CS261A PROJECT
#SIMPLIFIED INFLUENCE MAXIMIZATION(VERTEX COVER) PROBLEM

from igraph import *

overall_seed_sets = []
count = 0
count_p = 0
#####################################################################
##IMPLEMENTING "INFLUENCE SPREAD" BASED ON LINEAR THRESHOLD MODEL####
#####################################################################

def influence_spread(seed_set):
	
	inactive_nodes = []
	active_nodes = []
	return_set = []
	DG = G	
	for i in range(0,DG.vcount()):
		DG.vs[i]["state"] = "inactive"
	
	for i in range(0,len(seed_set)):
		DG.vs[seed_set[i]]["state"] = "active"
	
	while 1:
		for i in range(0,DG.vcount()):#detecting the inactive nodes
			if DG.vs[i]["state"] == "inactive":
				 inactive_nodes.append(i)
		active_nodes_number = DG.vcount() - len(inactive_nodes)#detecting initial active nodes
		
		for i in range(0,len(inactive_nodes)):#check all inactive nodes one by one
			neighbor_nodes = DG.neighbors(inactive_nodes[i], mode=ALL)
			count=0
			for j in range(0,len(neighbor_nodes)):#checking status of neighbors for each inactive nodes
				if( DG.vs[neighbor_nodes[j]]["state"] == "active"): count=count+1
			
			if count == len(neighbor_nodes):#if all neighbors are active then activate this inactive nodes	
				DG.vs[inactive_nodes[i]]["state"] = "active"		
		
		count2=0	
		for i in range(0,DG.vcount()):#count the number of active nodes after influence spreading
			if DG.vs[i]["state"] == "active":
				count2=count2+1
				active_nodes.append(i)
				

  		active_nodes_number2 = count2
		return_set = active_nodes
		inactive_nodes = []
		active_nodes = []	
		if active_nodes_number == active_nodes_number2:  break#if there is no change exit

	return return_set,active_nodes_number2#return the cost(total active nodes)

#################################################################
#######CONSTRUCTING INCLUSION/EXCLUSION BINARY TREE##############
#################################################################

def initialize():
	#Initializing binary tree
	binary_tree = Graph()
	binary_tree.add_vertices(1)#root node

	branch,from_ = [],[]
	branch.append(0)
	from_.append(None)
	binary_tree.vs["branch_nu"] = branch
 	binary_tree.vs["from"] = from_

	for i in range(0, G.vcount()):
		G.vs[i]["state"] = "inactive" 
	
	path_length = G.vcount() + 1 #max path length for DFBnB (+1 for root)

	node_types = []
	node_types.append("empty")
	binary_tree.vs["type"] = node_types


	return binary_tree,path_length

#################################################################
def add_node_labels(binary_tree):
	from_node =  binary_tree.vs[binary_tree.vcount()-1]["from"]  
	if binary_tree.vs[from_node]["branch_nu"] == 1:  
		binary_tree.vs[binary_tree.vcount()-1]["type"] = "inclusion"
	if binary_tree.vs[from_node]["branch_nu"] == 2:  	
		binary_tree.vs[binary_tree.vcount()-1]["type"] = "exclusion"
	
	return binary_tree

################################################################

def get_seed_set(search_tree):
	path = search_tree.get_shortest_paths(0,to=search_tree.vcount()-1,weights=None,mode=OUT,output="vpath")[0]
	seed_set = []
 	for i in range(0,len(path)):
		if search_tree.vs[path[i]]["type"] == "inclusion":
			seed_set.append(path[i]-1)
	return seed_set

################################################################

def get_new_activated(first,last):
	diff = []
	for i in range(0,len(last)):
		count = 0
		for j in range(0,len(first)):
			if first[j] != last[i]: count+=1
		if count == len(first): diff.append(last[i])

	return diff

###############################################################
def get_neighbors(vt):
	ne = G.incident(vt)
	edgelist = G.get_edgelist()
	nvt = []
	for i in range(0,len(ne)):
        	for j in range(0,2):
                	if edgelist[ne[i]][j] != vt:
				nvt.append(edgelist[ne[i]][j])

	return nvt

################################################################
############INCLUSION PRUNING###################################
################################################################
def prune(search_tree,nn):
	out = False
	for i in range(0,len(nn)):
		if nn[i] == search_tree.vcount()-1:
			search_tree.vs[search_tree.vcount()-1]["branch_nu"] = 1
	return search_tree
	
################################################################
#############EXCLUSION PRUNING##################################
################################################################

def prune2(search_tree,nn):
	out = False
	for i in range(0,len(nn)):
		if (nn[i]+1) == search_tree.vcount()-1:
			search_tree.vs[nn[i]]["branch_nu"] = 2
	return search_tree
	
######################################@#########################
#############NODE ORDERING HEURISTIC############################
################################################################

def order_nodes(G,f_nodes,t_nodes):
	ordered_index = []
	degrees = G.vs.degree()
	for i in range(0,len(degrees)):
		maxim = max(degrees)
		maxim_index = degrees.index(maxim)
		ordered_index.append(maxim_index)
		degrees.pop(maxim_index)
		degrees.insert(maxim_index,None)
	all_nodes = f_nodes+t_nodes
	for i in range(0,len(all_nodes)):
		temp = all_nodes[i]
		all_nodes[i] = ordered_index.index(temp)

	f_nodes = all_nodes[0:(len(all_nodes)/2)]
	t_nodes = all_nodes[(len(all_nodes)/2):len(all_nodes)]
	import copy
	OG = copy.copy(G)
	G = Graph(zip(f_nodes,t_nodes))
	return G,OG,ordered_index

####################################################################
##########SPANNING TREE  HEURISTIC EVALUATION FUNCTION##############
####################################################################
def get_heuristic_value(temp_G):
	ST = temp_G.spanning_tree( weights=None, return_tree = True )
	degrees = ST.vs.degree()	

	root = degrees.index(max(degrees))
	edgelist = ST.get_edgelist()

	for i in range(0,ST.vcount()):
		ST.vs[i]["parent"] = None

	parentlist = []
	ex = []
	parentlist.append(root)
	count = 0

	while 1:	
		for i in range(0,len(edgelist)):
			for j in range(0,len(edgelist[i])):
				if edgelist[i][j] == parentlist[0]:
					if j == 0:
						if (edgelist[i][j+1] in ex) == False:
							ST.vs[edgelist[i][j+1]]["parent"] = parentlist[0]
							count += 1
							if degrees[edgelist[i][j+1]] != 1:
								parentlist.append(edgelist[i][j+1])
					else:
						if(edgelist[i][j-1] in ex) == False:
							ST.vs[edgelist[i][j-1]]["parent"] = parentlist[0]
							count += 1
							if degrees[edgelist[i][j-1]] != 1:
								parentlist.append(edgelist[i][j-1])
		ex.append(parentlist[0])
		parentlist.pop(0)
		if count == (ST.vcount()-1):break


	for i in range(0,ST.vcount()):
		ST.vs[i]["ID"] = i
		ST.vs[i]["mark"] = False

	leaflist = []
	for i in range(0, len(degrees)):
		if degrees[i] == 1 : leaflist.append(i)


	GT = Graph()
	import copy
	GT = copy.copy(ST)

	while len(leaflist) != 0:
	
		f = leaflist[0]
		f_index = None
		leaflist.pop(0)
		tree_nodes = []
	
		for i in range(0,GT.vcount()):
			tree_nodes.append( GT.vs[i]["ID"] )

		first = f_index
	
		for i in range(0,len(tree_nodes)):
			if f == GT.vs[i]["ID"]:
				f_index = i

		if f in tree_nodes:

			if ST.vs[f]["mark"] == False and GT.vs[f_index]["parent"] == None:
				ST.vs[f]["mark"] = True


			elif ST.vs[f]["mark"] == False and GT.vs[f_index]["parent"] != None:
				ST.vs[GT.vs[f_index]["parent"]]["mark"] = True

			parent = GT.vs[f_index]["parent"]
			children = []
			for i in range(0,GT.vcount()):
				if (f_index != i) and (GT.vs[i]["parent"] == parent):
					children.append(GT.vs[i]["ID"])
		
			GT.delete_vertices(f_index)
			if parent != root and len(children) == 0:
				leaflist.append(parent)
	
	vc_count = 0
	for i in range(0,ST.vcount()):
		if ST.vs[i]["mark"] == True: 
			vc_count += 1
	return vc_count

#############################################################
##########DFBnB WITH PRUNING AND NODE ORDERING###############
#############################################################
def DFBnB_Doublepruning(search_tree,path_length,bound,overall_seed_sets,degrees,partial_vc):
	counter = 0

	for i in range(0,search_tree.vcount()):
		if search_tree.vs[i]["branch_nu"] == 2: counter+=1

	best = float("inf") 
	h_n = 0	
	while search_tree.vcount() != counter:#loop until all internal nodes have two children
		get_out = False
		while search_tree.vcount() < path_length:#Run in linear space(path_length)

			total_degrees = sum(degrees)		
			search_tree.add_vertices(1)
		
			from_node = search_tree.vcount() - 2
			to_node = search_tree.vcount() - 1
			search_tree.vs[to_node]["from"] = from_node
			search_tree.add_edges( (from_node, to_node) )
			search_tree.vs[from_node]["branch_nu"] += 1 
 			search_tree.vs[to_node]["branch_nu"] = 0
			search_tree = add_node_labels(search_tree)
			inv_depth = G.vcount()-search_tree.vcount()+1
			partial_seed = []
			for i in range(1,search_tree.vcount()):
				if search_tree.vs[i]["type"] == "inclusion":
					partial_seed.append(i-1)
				else:
                                        total_degrees -= degrees[i-1]

#########################CALLING HEURISTIC EVALUATION FUNCTION############

			covered_nodes = []	
			for i in range(0,len(partial_seed)):
				covered_nodes.append( partial_seed[i])
			
			temp_G = Graph()
			import copy
			temp_G = copy.copy(G)
			temp_G.delete_vertices(covered_nodes)
			temp_degrees = temp_G.degree()
			lonely = []
			for i in range(0,len(temp_degrees)):
				if temp_degrees[i] == 0:
					lonely.append(i)
			temp_G.delete_vertices(lonely)
			con_com = temp_G.decompose(mode=1)
			old_hn = h_n
			h_n = 0		
			if temp_G.vcount() == 0 : h_n =0
			else:
				for i in range(0,len(con_com)):
					if con_com[i].vcount() < 4 : h_n += 1
					elif con_com[i].vcount() > 3 and con_com[i].vcount() < 7:
						h_n += 2
					elif con_com[i].vcount() > 6 and con_com[i].vcount() < 11:
						h_n += 3
					else : h_n += get_heuristic_value(con_com[i])
			g_n = len(partial_seed)
			new = []
			f_n = g_n + h_n
	
###############################################################

			if bound == g_n:# BOUND
				break
		
			if f_n > best:
				break
			
			if total_degrees <= G.ecount():
                               break

			activated_nodes = influence_spread(partial_seed)[0]
			new_activated = get_new_activated(partial_seed, activated_nodes)
			search_tree = prune(search_tree,new_activated)#inclusion pruning
		
			exc_nodes = []
			for i in range(1,search_tree.vcount()):
				if search_tree.vs[i]["type"] == "exclusion":
					exc_nodes.append(i-1)
			
			neighbor_nodes =[]
			for i in range(0,len(exc_nodes)):
				temp = get_neighbors(exc_nodes[i])
				for j in range(0,len(temp)):
					if (temp[j] in neighbor_nodes) == False and (temp[j] in exc_nodes) == False:	
						neighbor_nodes.append(temp[j])

			search_tree = prune2(search_tree,neighbor_nodes)#exclusion pruning

				
		
		old_best = best
		overall_seed_sets.append(get_seed_set(search_tree))
		out,best = print_result2("DFBnB_Doublepruning",overall_seed_sets,partial_vc)
		if best > old_best: best = old_best
		overall_seed_sets = []

#		if out == True : break

		backtrack = 0
		for i in range(search_tree.vcount()-2,-1,-1):
			if search_tree.vs[i]["branch_nu"] != 2:
				backtrack = i
				break
		for i in range(search_tree.vcount()-1,backtrack,-1):
			search_tree.delete_vertices(i)

		counter = 0
		for i in range(0,search_tree.vcount()):
			if search_tree.vs[i]["branch_nu"] == 2: counter+=1

################################################################
##########BRUTE FORCE SEARCH####################################
################################################################

def DFBnB_brute(search_tree,path_length,overall_seed_sets):
	counter = 0
	for i in range(0,search_tree.vcount()):
		if search_tree.vs[i]["branch_nu"] == 2: counter+=1

	while search_tree.vcount() != counter:
		while search_tree.vcount() < path_length:
			search_tree.add_vertices(1)
		
			from_node = search_tree.vcount() - 2
			to_node = search_tree.vcount() - 1
		
			search_tree.vs[to_node]["from"] = from_node
			search_tree.add_edges( (from_node, to_node) )
			search_tree.vs[from_node]["branch_nu"] += 1 
 			search_tree.vs[to_node]["branch_nu"] = 0
		
		search_tree = add_node_labels(search_tree)
		overall_seed_sets.append(get_seed_set(search_tree))
		print_result2("Brute_Force",overall_seed_sets)
		overall_seed_sets = []
		
		backtrack = 0
		for i in range(search_tree.vcount()-2,-1,-1):
			if search_tree.vs[i]["branch_nu"] != 2:
				backtrack = i
				break
		for i in range(search_tree.vcount()-1,backtrack,-1):
			search_tree.delete_vertices(i)

		counter = 0
		for i in range(0,search_tree.vcount()):
			if search_tree.vs[i]["branch_nu"] == 2: counter+=1

#############################################################
	
def print_result2(select,overall_seed_sets,partial_vc):
	global count
	global count_p
	count_p+=1
	out = False
	best = float("inf")		
	for i in range(0,len(overall_seed_sets)):
		nodes,k = influence_spread(overall_seed_sets[i])
		if k == G.vcount() :
			count +=1
			last_seed = []
			if select == "Brute_Force":
				for j in range(0,len(overall_seed_sets[i])):
					last_seed.append(overall_seed_sets[i][j])
			else:
				for j in range(0,len(overall_seed_sets[i])):
					last_seed.append(G.vs[ordered_index[overall_seed_sets[i][j]]]["actual_name"])
			
			if select == "Brute_Force" :
				if len(last_seed) == bound :print count,':',last_seed,'length:',len(last_seed)
			else : 
				print count,':',(last_seed+partial_vc),'length:',len(last_seed+partial_vc)
				out = True
				best = len(last_seed)
	
	return out,best
##############################################################
###########################PRE-EVALUATION FUNCTION############
##############################################################

def pre_evaluation(G):
	
	for i in range(0,G.vcount()):
		G.vs[i]["actual_name"] = i

	final_partial_vc = []
	degrees = G.vs.degree()
	min_element = min(degrees)	
	count = 0	
	while (min_element > 1) == False:
		partial_vc = []
		leaves = []
		for i in range(0,len(degrees)):
			if degrees[i] == 1: leaves.append(i)
		edgelist = G.get_edgelist()
		for i in range(0,len(edgelist)):
			for j in range(0,len(edgelist[i])):
				if (edgelist[i][j] in leaves) == True:
					if j==1 and (edgelist[i][j-1] in partial_vc) == False:
						partial_vc.append(edgelist[i][j-1])
					elif j ==0 and (edgelist[i][j+1] in partial_vc) == False:
						partial_vc.append(edgelist[i][j+1])

		G.delete_vertices(leaves+partial_vc)
		for i in range(0,len(partial_vc)): 
			final_partial_vc.append(partial_vc[i])
		degrees = G.vs.degree()
		if len(degrees) != 0:
			min_element = min(degrees)
		if len(degrees) == 0 or min_element == 0: min_element = 2
		print count ,'-',min_element 
		count += 1

	nn = G.vs.degree()
	while (0 in nn): 
		G.delete_vertices(nn.index(0))
		nn = G.vs.degree()

	n_edgelist = G.get_edgelist()
	unzip = lambda l:tuple(zip(*l))
	if len(n_edgelist) != 0:
		new_f_nodes = unzip(n_edgelist)[0]
		new_t_nodes = unzip(n_edgelist)[1]
	else:
		new_f_nodes = []
		new_t_nodes = []

	return G,final_partial_vc,new_f_nodes,new_t_nodes

################################################################
#######BUILDING SOCIAL NETWORK AND SETTING THEIR STATES#########
################################################################ 

if __name__ == "__main__":

	import csv
	with open('test_graphs/graphs/graph_random150.csv', 'rb') as f:#read graph data from .csv file
		reader = csv.reader(f)
		reader.next()
		f_nodes = []
		t_nodes = []
		for row in reader:
			f_nodes.append(int(row[0]))
			t_nodes.append(int(row[1]))
	G = Graph(zip(f_nodes,t_nodes))
	G,partial_vc,f_nodes,t_nodes = pre_evaluation(G)
	if G.vcount() == 0:
		print partial_vc
		import sys
		sys.exit()

	G,OG,ordered_index = order_nodes(G,list(f_nodes),list(t_nodes))#order the nodes
	for i in range(0,G.vcount()):
		G.vs[ordered_index[i]]["actual_name"] = OG.vs[i]["actual_name"]
	degrees = G.vs.degree()
	print 'total',sum(degrees),'ecount:',G.ecount(),'vcount:',G.vcount()
	count_p=0
	count=0	
	print 'DFBnB with Spanning Tree Heuristic RESULTS :'
	print '---------------------------------------------'
	overall_seed_sets = []	
	inc_exc_tree, path_length = initialize()
	bound = 129-len(partial_vc) # budget to cover all nodes
	DFBnB_Doublepruning(inc_exc_tree,path_length,bound,overall_seed_sets,degrees,partial_vc)
	print 'Total tested seed set:',count_p
	pn = count_p
	bn = 2**G.vcount()
	print 'The percentage of pruning in entire tree: %',(float(bn-pn)/bn)*100