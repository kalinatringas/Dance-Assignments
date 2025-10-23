import random
import csv  
import io
import sys
from contextlib import redirect_stdout
import pandas as pd
from typing import List, Dict
from collections import defaultdict

class DanceScheduler:
    def __init__(self, dancers: Dict[str, Dict], dance_capacities: Dict[str, int]):
        """
        reformat inputs in order to satisfy 
        {
            'Dancer Name': {
                'desired_count': 3,  # How many dances they want
                'ranked_choices': ['Dance A', 'Dance B', 'Dance C', 'Dance D', 'Dance E']
            }
        }
        {
            'Capacities' :{
                'ABC': 5
                'DEF': 12
                }
        }
        
        """

        self.dancers = dancers
        self.dance_capacities = dance_capacities or {}
        self.all_dances = self._get_all_dances()

    @classmethod
    def from_csv(cls, filename: str, capacities_file: str = None):
            #columns_to_keep = ["Name?", "How many showcase sets do you want to be in? ","one","two","three", "four", "five"]
        data = pd.read_csv(filename)
        data.columns = data.columns.str.strip()

        # Detect which columns are dance choices (e.g., "one", "two", "three", etc.)
        choice_columns = [col for col in data.columns if col.lower().startswith("choice") or col.lower() in {"one", "two", "three", "four", "five"}]

    # data = pd.read_csv("input.csv", usecols=columns_to_keep)

        dancers = {}
        for __, row in data.iterrows():
            dancer_name = row["Name?"]
            desired_count = int(row["How many showcase sets do you want to be in?"])

            ranked_choices = [row[col] for col in choice_columns if pd.notna(row[col])]
            
            # print(f"\nDancer: {dancer_name}")
            # print(f"Desired count: {desired_count}")
            # print(f"Ranked choices: {ranked_choices}")

            dancers[dancer_name]= {
                "desired count": desired_count,
                "ranked choices": ranked_choices
            }
        cap = pd.read_csv(capacities_file)
        cap.columns = cap.columns.str.strip()  # Remove any whitespace from column names
        capacities = {}
        for __, row in cap.iterrows():
            dance_name = row["Dance Name"].strip()  # Remove any whitespace from dance names
            capacity = int(row["Dancer Count"])
            capacities[dance_name] = capacity
        return cls(dancers, capacities)
    
    def _get_all_dances(self):
        dances = set()
        for prefs in self.dancers.values():
            dances.update(prefs['ranked choices'])
        return dances

    def _calculate_satisfaction(self, assignment: Dict[str, List[str]]) -> float:
        #Calculate how well an assignment satisfies preferences.
        total_score = 0
        for dancer, dances in assignment.items():
            ranked = self.dancers[dancer]['ranked choices']
            for dance in dances:
                if dance in ranked:
                    # Higher score for higher-ranked choices (inverse of index)
                    rank_score = len(ranked) - ranked.index(dance)
                    total_score += rank_score
        return total_score
    
    def _is_valid_assignment(self, assignmnet: Dict[str, List[str]]) -> bool:
        #check to see if each dancer has their desired count
        for dancer, dances in assignmnet.items():
            desired = self.dancers[dancer]["desired count"]
            if len(dances) != desired:
                print(f"Invalid: Dancer {dancer} has {len(dances)} dances but wants {desired}")
                return False
        
        if self.dance_capacities:
            dance_counts = defaultdict(int)
            for dances in assignmnet.values():
                for dance in dances:
                    dance_counts[dance] += 1
            
            for dance, count in dance_counts.items():
                if dance in self.dance_capacities:
                    if count > self.dance_capacities[dance]:
                        print(f"Invalid: Dance {dance} has {count} dancers but capacity is {self.dance_capacities[dance]}")
                        return False
            
            # Print dance counts for debugging
            print("\nDance assignments:")
            for dance, count in dance_counts.items():
                capacity = self.dance_capacities.get(dance, "No limit")
                print(f"{dance}: {count}/{capacity}")
        
        return True

    
    def _generate_greedy_config(self, seed: int = None) -> Dict[str, List[str]] :
        #Makes a greedy configuration using greedy selection with rand
        if seed is not None:
            random.seed(seed)
        assignments = defaultdict(list)
        dance_counts = defaultdict(int) #tracks how many dancers are in each dance
        selections = []
        # Create list of (dancer, preference_index) to process
        for dancer, prefs in self.dancers.items():
            desired = prefs['desired count']
            ranked = prefs['ranked choices']

            #selection with some random indicies
            indices = list(range(min(desired * 3, len(ranked))))
            random.shuffle(indices)
            selections.extend([(dancer, i) for i in indices[:desired*2]])
        random.shuffle(selections)
         # now assign dances acording to capacity constraints
        for dancer, pref_idx in selections:
            if len(assignments[dancer]) < self.dancers[dancer]['desired count']:
                ranked = self.dancers[dancer]['ranked choices']
                if pref_idx < len(ranked):
                    dance = ranked[pref_idx]
                    
                    if dance in assignments[dancer]:
                        continue
                    if self.dance_capacities and dance in self.dance_capacities:
                        if dance_counts[dance] >= self.dance_capacities[dance]:
                            continue

                    assignments[dancer].append(dance)
                    dance_counts[dance]+=1
        #now fill in the remaining slots
        for dancer, prefs in self.dancers.items():
            desired = prefs["desired count"]
            while len(assignments[dancer])<desired:
                assigned = False
                for dance in prefs["ranked choices"]:
                    if dance not in assignments[dancer]:
                        if self.dance_capacities and dance in self.dance_capacities:
                            if dance_counts[dance] >= self.dance_capacities[dance]:
                                continue
                        assignments[dancer].append(dance)
                        dance_counts[dance]+=1
                        assigned = True
                        break
                if not assigned:
                    break
        return dict(assignments)
    def generate_configurations(self, n:int=5 ) -> List[Dict[str, List[str]]]:
        configs = []
        attempts = 0
        max_attempts = n*10
        while len(configs) < n and attempts < max_attempts:
            config = self._generate_greedy_config(seed=attempts)
            if not any(self._configs_equal(config, c) for c in configs):
                configs.append(config)
            attempts += 1
        configs.sort(key=lambda c: self._calculate_satisfaction(c), reverse = True) #list by best configurations

        return configs
    def _return_violations(self, config: Dict[str, List[str]], config_num: int = None) -> str :
        violations = ''
        for dancer, dances in config.items():
            desired = self.dancers[dancer]["desired count"]
            if len(dances) != desired:
                violations+=(f"\n! {dancer} has {len(dances)} dances but wanted {desired}")
            
        if self.dance_capacities:
            dance_counts = defaultdict(int)
            for dances in config.values():
                for dance in dances:
                    dance_counts[dance] += 1
            
            for dance, count in dance_counts.items():
                if dance in self.dance_capacities:
                    if count > self.dance_capacities[dance]:
                        violations+=(f"\n! {dance} has {count} dancers but capacity is {self.dance_capacities[dance]}")
        
        return violations

    def _configs_equal(self, c1: Dict[str, List[str]], c2: Dict[str, List[str]]) -> bool:
        # checks to see if two configs are equal
        if set(c1.keys())!= set(c2.keys()): #checks to see if both configs have the same dancers
            return False
        for dancer in c1: #then for each dancer, check to see if the set of assigned dances are the same
            if set(c1[dancer]) != set(c2[dancer]):
                return False
        return True

        
    def print_configuration(self, config: Dict[str, List[str]], config_num: int = None):
        
        if config_num is not None:
            print(f"\n{'='*50}")
            print(f"Configuration {config_num}")
            print(f"Satisfaction Score: {self._calculate_satisfaction(config):.1f}")
            print(f"{'='*50}")
        
        #print constraint violations
        print("\nConstraint Status:")
        violations = [] #could I return violations as a member of the class or 
        
        # check dancer count constraints
        for dancer, dances in config.items():
            desired = self.dancers[dancer]["desired count"]
            if len(dances) != desired:
                violations.append(f"! {dancer} has {len(dances)} dances but wanted {desired}")
        
        # check dance capacity constraints
        if self.dance_capacities:
            dance_counts = defaultdict(int)
            for dances in config.values():
                for dance in dances:
                    dance_counts[dance] += 1
            
            for dance, count in dance_counts.items():
                if dance in self.dance_capacities:
                    if count > self.dance_capacities[dance]:
                        violations.append(f"! {dance} has {count} dancers but capacity is {self.dance_capacities[dance]}")
        
        if violations:
            print("Issues found:")
            for violation in violations:
                print(violation)
        else:
            print("* All constraints satisfied")
        
        # Organize dancers by dance
        dance_to_dancers = defaultdict(list)
        for dancer, dances in config.items():
            for dance in dances:
                rank = self.dancers[dancer]["ranked choices"].index(dance) + 1 if dance in self.dancers[dancer]["ranked choices"] else 0
                dance_to_dancers[dance].append((dancer, rank))

        print("\nDance Assignments:")
        for dance in sorted(self.all_dances):
            if dance in dance_to_dancers:
                dancers_in_dance = dance_to_dancers[dance]
                capacity = self.dance_capacities.get(dance, "No limit")
                print(f"\n{dance} ({len(dancers_in_dance)} dancers, capacity: {capacity}):")
                
                # Sort dancers by their preference rank for this dance
                dancers_in_dance.sort(key=lambda x: (x[1] if x[1] > 0 else float('inf')))
                
                for dancer, rank in dancers_in_dance:
                    if rank > 0:
                        print(f"  * {dancer} (Choice #{rank})")
                    else:
                        print(f"  - {dancer} (Not in preferences)")
        
        if self.dance_capacities:
            print(f"\n{'-'*50}")
            print("Dance Capacity Usage:")
            dance_counts = defaultdict(int)
            for dances in config.values():
                for dance in dances:
                    dance_counts[dance] += 1
            for dance in sorted(self.all_dances):
                count = dance_counts[dance]
                capacity = self.dance_capacities.get(dance, "No limit")
                if isinstance(capacity, int):
                    status = "OVER CAPACITY" if count > capacity else "FULL" if count == capacity else "OK"
                    status_symbol = "!" if count > capacity else "*"
                    print(f"   {status_symbol} {dance}: {count}/{capacity} [{status}]")
                else:
                    print(f"   {dance}: {count}/{capacity}")


    def configuration_report(self, config: Dict[str, List[str]], config_num: int = None) -> str:
        """Return the same human-readable report as `print_configuration`, but as a string."""
        lines = []
        def w(s=""):
            lines.append(str(s))

        if config_num is not None:
            w('\n' + '='*50)
            w(f"Configuration {config_num}")
            w(f"Satisfaction Score: {self._calculate_satisfaction(config):.1f}")
            w('='*50)

        # Constraint status
        w('\nConstraint Status:')
        violations = []

        for dancer, dances in config.items():
            desired = self.dancers[dancer]["desired count"]
            if len(dances) != desired:
                violations.append(f"! {dancer} has {len(dances)} dances but wanted {desired}")

        if self.dance_capacities:
            dance_counts = defaultdict(int)
            for dances in config.values():
                for dance in dances:
                    dance_counts[dance] += 1

            for dance, count in dance_counts.items():
                if dance in self.dance_capacities and count > self.dance_capacities[dance]:
                    violations.append(f"! {dance} has {count} dancers but capacity is {self.dance_capacities[dance]}")

        if violations:
            w('Issues found:')
            for v in violations:
                w(v)
        else:
            w('* All constraints satisfied')

        # Organize dancers by dance
        dance_to_dancers = defaultdict(list)
        for dancer, dances in config.items():
            for dance in dances:
                rank = self.dancers[dancer]["ranked choices"].index(dance) + 1 if dance in self.dancers[dancer]["ranked choices"] else 0
                dance_to_dancers[dance].append((dancer, rank))

        w('\nDance Assignments:')
        for dance in sorted(self.all_dances):
            if dance in dance_to_dancers:
                dancers_in_dance = dance_to_dancers[dance]
                capacity = self.dance_capacities.get(dance, "No limit")
                w(f"\n{dance} ({len(dancers_in_dance)} dancers, capacity: {capacity}):")
                dancers_in_dance.sort(key=lambda x: (x[1] if x[1] > 0 else float('inf')))
                for dancer, rank in dancers_in_dance:
                    if rank > 0:
                        w(f"  * {dancer} (Choice #{rank})")
                    else:
                        w(f"  - {dancer} (Not in preferences)")

        if self.dance_capacities:
            w('\n' + '-'*50)
            w('Dance Capacity Usage:')
            dance_counts = defaultdict(int)
            for dances in config.values():
                for dance in dances:
                    dance_counts[dance] += 1
            for dance in sorted(self.all_dances):
                count = dance_counts[dance]
                capacity = self.dance_capacities.get(dance, "No limit")
                if isinstance(capacity, int):
                    status = "OVER CAPACITY" if count > capacity else "FULL" if count == capacity else "OK"
                    status_symbol = "!" if count > capacity else "*"
                    w(f"   {status_symbol} {dance}: {count}/{capacity} [{status}]")
                else:
                    w(f"   {dance}: {count}/{capacity}")

        return "\n".join(lines)



if __name__ == "__main__":
    dancers = 'dances.csv'

    scheduler = DanceScheduler.from_csv('input.csv', 'dances.csv')
    configs = scheduler.generate_configurations(n=5)
    violations = scheduler._return_violations(configs)

    for i, config in enumerate(configs, 1):
        scheduler.print_configuration(config, config_num=i)

    print(f"\n{'='*50}")
    print(f"Generated {len(configs)} different configurations")
    print(f"{'='*50}")