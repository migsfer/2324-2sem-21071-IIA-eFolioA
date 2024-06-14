#!/usr/bin/python
'''========================================================================
Name        : efolioA.py
Date        : 11.04.2024
Date-of-FIX : 14.06.2024

NOTAS       :


python efolioA.py
============================================================================
'''
import os
import sys
from itertools import permutations
from functools import partial
from collections import deque
import time
from itertools import combinations_with_replacement


def menu():
    choice = ''
    print("\n")
    print('-' * 80)
    print("Bem-vindo ao Programa")
    print('-' * 80)
    print("1. Escolher Mapa a Correr A")
    print("2. Escolher Mapa a Correr B")
    print("3. Correr Todos os Mapas")
    print("\nQ. Quit.\n")

    while choice not in ['1', '2', '3', 'q', 'Q']:
        choice = input("Enter your choice:[1-3](q to quit) ").lower()
    return choice


def mapchoice(prompt, comprido):
    choice = 'N/A'
    lim_min = 0

    while choice.isdigit() is False or (int(choice) not in range(lim_min+1, comprido + 1)):
        choice = input(prompt)
        if choice.isdigit() is False:
            print("NOT A NUMBER")
        elif choice.isdigit() is True:
            if int(choice) not in range(lim_min+1, comprido+1):
                print("NOT IN RANGE[", lim_min+1, "-", comprido, "]")
                choice = 'N/A'
    return int(choice) - 1


def calculate_sum(Zona, ZoneCenters):
    SomaTotal = 0
    counted_cells = [[False] * len(Zona[0]) for _ in range(len(Zona))]

    for centro_row, centro_col, raios in ZoneCenters:
        for i in range(centro_row - raios, centro_row + raios + 1):
            for j in range(centro_col - raios, centro_col + raios + 1):
                if 0 <= i < len(Zona) and 0 <= j < len(Zona[0]) and not counted_cells[i][j]:
                    SomaTotal += Zona[i][j]
                    counted_cells[i][j] = True

    return SomaTotal


def total_quantity(solution, delegacias):
    return sum(delegacias[p]['raioProt'] for p in solution)


def discard_inferior_tuples(tuples):
    dimensions = [(len(t)*(2*int(max(t))+1), 2*int(max(t))+1) for t in tuples]
    results = []

    for i in range(len(tuples)):
        inferior = False
        for j in range(len(tuples)):
            if i == j:
                continue
            if dimensions[i][0] <= dimensions[j][0] and dimensions[i][1] <= dimensions[j][1]:
                inferior = True
                break
        if not inferior:
            results.append(tuples[i])

    return results


def GeraRaiosProt(Verba):
    delegacias = {
        '1': {'cost': 4, 'raioProt': 9},
        '2': {'cost': 5, 'raioProt': 25},
        '3': {'cost': 9, 'raioProt': 49},
        '4': {'cost': 17, 'raioProt': 81}
    }
    Lstfinal_raiosProt = []
    valid_raiosProt = set()

    for NRraios in range(1, Verba + 1):
        found_valid_solution = False
        for perm in combinations_with_replacement(delegacias.keys(), NRraios):
            total_cost = sum(delegacias[p]['cost'] for p in perm)
            if total_cost <= Verba:
                valid_raiosProt.add(tuple(sorted(perm)))
                found_valid_solution = True
            elif total_cost > Verba and not found_valid_solution:
                break
        if not found_valid_solution:
            break
    for solution in valid_raiosProt:
        total_cost = sum(delegacias[p]['cost'] for p in solution)
        if total_cost <= Verba:
            Lstfinal_raiosProt.append(solution)

    # Sorting Lstfinal_raiosProt by length in descending order
    Lstfinal_raiosProt.sort(key=len, reverse=True)

    # Eliminate sets with inferior sums for each length
    unique_lengths = set(len(solution) for solution in Lstfinal_raiosProt)
    for length in unique_lengths:
        solutions_same_length = [solution for solution in Lstfinal_raiosProt if len(solution) == length]
        max_sum = max(total_quantity(solution, delegacias) for solution in solutions_same_length)
        Lstfinal_raiosProt = [solution for solution in Lstfinal_raiosProt if not (len(solution) == length and total_quantity(solution, delegacias) < max_sum)]

    # Sort final descendente(reverse=True) por maior soma de raios de protecao
    SomaTotalProtecaoDoRaio = partial(total_quantity, delegacias=delegacias)
    Lstfinal_raiosProt.sort(key=SomaTotalProtecaoDoRaio, reverse=True)

    # Swap the first two sets if one of them has an inferior length
    if len(Lstfinal_raiosProt) >= 2:
        if len(Lstfinal_raiosProt[0]) > len(Lstfinal_raiosProt[1]):
            Lstfinal_raiosProt[0], Lstfinal_raiosProt[1] = Lstfinal_raiosProt[1], Lstfinal_raiosProt[0]

    return discard_inferior_tuples(Lstfinal_raiosProt)


def PrintFinalZona(Zona, Objectivo, ZoneCenters, SomaTotal, Generations, Expansions, MapaId):
    linhas = " ----- " * len(Zona[0]) + " "
    HeadQ = "H"
    raio_symbol = "+"

    print(linhas)
    for i, row in enumerate(Zona):
        row_str = ""
        for j, val in enumerate(row):
            if (i, j) in [(center_row, center_col) for center_row, center_col, _ in ZoneCenters]:
                symbol = HeadQ
            elif any(abs(i - center_row) <= raios and abs(j - center_col) <= raios for center_row, center_col, raios in ZoneCenters):
                symbol = raio_symbol
            else:
                symbol = " "
            row_str += f"| {val:3} {symbol}"
        row_str += "|"
        print(row_str)
        print(linhas)

    print(f"\nMapaID: {MapaId[0]} - {MapaId[1]}")
    print(f"Delegacias Colocadas: {len(ZoneCenters)}")
    for center_row, center_col, raios in ZoneCenters:
        print(f"Centro: ({center_row}, {center_col}) Raio: {raios}")

    print(f"\nProtegidos: {SomaTotal} / {Objectivo}")
    print(f"Nr. Gerações: {Generations}")
    print(f"Nr. Expansões: {Expansions}")


def loadZone(file_path):
    LstZonas = []
    zona = []

    with open(file_path, 'r') as file:
        zonas = file.read()

    ZonaRows = zonas.split('\n{')
    ZonaRows = [s for s in ZonaRows if "\n/" not in s]
    ZonaRows = [s for s in ZonaRows if "{" not in s]

    for zonaLinhaStr in ZonaRows:
        if zonaLinhaStr.find("\n}") != -1:
            row = zonaLinhaStr.split('},')[0]
            if row:
                currntrow = list(map(int, row.split(',')))
                zona.append(currntrow)
            LstZonas.append(zona)
            zona = []
        else:
            row = zonaLinhaStr.split('},')[0]
            if row:
                currntrow = list(map(int, row.split(',')))
                zona.append(currntrow)
    return LstZonas


def ProcuraCegaLargura(Zona, Objectivo, ZoneCenters, Generations, Expansions):
    Queue = deque([(ZoneCenters, calculate_sum(Zona, ZoneCenters))])
    seen = set()

    while Queue:
        current_zone_centers, total_sum = Queue.popleft()
        if total_sum >= Objectivo:
            return current_zone_centers, total_sum, Generations, Expansions
        Expansions += 1

        for i in range(len(current_zone_centers)):
            centro_row, centro_col, raio = current_zone_centers[i]
            # Gerador direita e baixo e adiciona para direita da fila
            for dr, dc in [(1, 0), (0, 1)]:
                new_center_row, new_center_col = centro_row + dr, centro_col + dc
                new_zone_centers = current_zone_centers[:]
                if (0 <= new_center_row - raio) and (new_center_row + raio < len(Zona)) and (0 <= new_center_col - raio) and (new_center_col + raio < len(Zona[0])):
                    if (new_center_row, new_center_col, raio) not in new_zone_centers:
                        new_zone_centers[i] = (new_center_row, new_center_col, raio)
                        new_zone_centers_tpl = tuple(new_zone_centers)
                        if (new_zone_centers_tpl, calculate_sum(Zona, new_zone_centers_tpl)) not in seen:
                            Queue.appendleft((new_zone_centers, calculate_sum(Zona, new_zone_centers)))
                            perms = permutations(new_zone_centers)
                            perms_list = [list(perm) for perm in perms]
                            for perm in perms_list:
                                all_equal = all(tpl1[-1] == tpl2[-1] for tpl1, tpl2 in zip(perm, new_zone_centers))
                                if all_equal and new_zone_centers_tpl not in seen:
                                    new_zone_centers_tpl = tuple(perm)
                                    seen.add((new_zone_centers_tpl, calculate_sum(Zona, new_zone_centers_tpl)))
                                    Generations += 1
            # Gerador esquerda e cima e adiciona para esquerda da fila
            for dr, dc in [(0, -1), (-1, 0)]:
                new_center_row, new_center_col = centro_row + dr, centro_col + dc
                new_zone_centers = current_zone_centers[:]
                if (0 <= new_center_row - raio) and (new_center_row + raio < len(Zona)) and (0 <= new_center_col - raio) and (new_center_col + raio < len(Zona[0])):
                    if (new_center_row, new_center_col, raio) not in new_zone_centers:
                        new_zone_centers[i] = (new_center_row, new_center_col, raio)
                        new_zone_centers_tpl = tuple(new_zone_centers)
                        if (new_zone_centers_tpl, calculate_sum(Zona, new_zone_centers_tpl)) not in seen:
                            Queue.appendleft((new_zone_centers, calculate_sum(Zona, new_zone_centers)))
                            perms = permutations(new_zone_centers)
                            perms_list = [list(perm) for perm in perms]
                            for perm in perms_list:
                                all_equal = all(tpl1[-1] == tpl2[-1] for tpl1, tpl2 in zip(perm, new_zone_centers))
                                if all_equal and new_zone_centers_tpl not in seen:
                                    new_zone_centers_tpl = tuple(perm)
                                    seen.add((new_zone_centers_tpl, calculate_sum(Zona, new_zone_centers_tpl)))
                                    Generations += 1

    return [], 0, Generations, Expansions


def main():
    fnZones = "zonas.txt"
    params = {
            '1': {'Verba': 4, 'A': 19, 'B': 20},
            '2': {'Verba': 4, 'A': 21, 'B': 22},
            '3': {'Verba': 8, 'A': 67, 'B': 68},
            '4': {'Verba': 8, 'A': 59, 'B': 60},
            '5': {'Verba': 12, 'A': 125, 'B': 126},
            '6': {'Verba': 12, 'A': 57, 'B': 58},
            '7': {'Verba': 16, 'A': 140, 'B': 141},
            '8': {'Verba': 16, 'A': 93, 'B': 94},
            '9': {'Verba': 20, 'A': 211, 'B': 212},
            '10': {'Verba': 20, 'A': 125, 'B': 126}
            }
    LstZones = loadZone(os.path.join(sys.path[0], fnZones))
    Generations = 0
    Expansions = 0
    ZoneCenters = []
    RaiosLst = []
    i = 1

    while True:
        choice = menu()
        if choice == '1':
            MapV = 'A'
            print("\033[H\033[J", end="")  # clear screen
            mchoice = mapchoice("Qual o mapa ?  ", len(LstZones))
            Zona = LstZones[mchoice]
            mchoice = str(mchoice + 1)
            print("\n", '-' * 80)
            current_time = time.localtime()
            print(f"Current time: {time.strftime('%H:%M:%S', current_time)}")

            Verba = params[mchoice]['Verba']
            Objectivo = params[mchoice][MapV]
            start_time = time.time()
            print(mchoice, MapV, Objectivo, Verba)

            RaiosLst = GeraRaiosProt(Verba)

            for RaiosTuple in RaiosLst:
                if not RaiosTuple:  # Salta vazios
                    continue

                # Converte raios em inteiros
                raios = tuple(map(int, RaiosTuple))

                for raio in raios:
                    centro_row = raio
                    centro_col = raio
                    if (centro_row, centro_col, raio) in ZoneCenters:
                        centro_row = len(Zona) - raio -1
                        centro_col = raio
                    if (centro_row, centro_col, raio) in ZoneCenters:
                        centro_row = raio
                        centro_col = len(Zona[-1]) - raio -1
                    if (centro_row, centro_col, raio) in ZoneCenters:
                        centro_row = len(Zona) - raio -1
                        centro_col = len(Zona[-1]) - raio -1
                    while (centro_row, centro_col, raio) in ZoneCenters:
                        # Verifica o resto das colisoes e ajusta centro para +1+1 diagonal
                        if centro_col + 1 < len(Zona[0]):
                            centro_col += 1
                        else:
                            centro_row += 1
                            centro_col = raio
                    ZoneCenters.append((centro_row, centro_col, raio))

                # ProcuraCegaLargura para cada RaiosTuple
                solution, total_sum, Generations, Expansions = ProcuraCegaLargura(Zona, Objectivo, ZoneCenters, Generations, Expansions)

                if solution:
                    PrintFinalZona(Zona, Objectivo, solution, total_sum, Generations, Expansions, (mchoice, MapV))
                    break
                ZoneCenters = []  # Reset ZoneCenters for the next RaiosTuple

            ZoneCenters = []  # Reset ZoneCenters for the next RaiosTuple
            # solution = []
            total_sum = 0
            Generations = 0
            Expansions = 0
            end_time = time.time()
            execution_time = end_time - start_time
            minutes = int(execution_time // 60)
            seconds = int(execution_time % 60)
            print("Tempo exec: {} min(s) e {} seg(s)".format(minutes, seconds))

            if not solution:
                print("***NO SOLUTION FOUND.***")

        elif choice == '2':
            MapV = 'B'
            print("\033[H\033[J", end="")  # clear screen
            mchoice = mapchoice("Qual o mapa ?  ", len(LstZones))
            Zona = LstZones[mchoice]
            mchoice = str(mchoice + 1)
            print("\n", '-' * 80)
            current_time = time.localtime()
            print(f"Current time: {time.strftime('%H:%M:%S', current_time)}")

            Verba = params[mchoice]['Verba']
            Objectivo = params[mchoice][MapV]
            start_time = time.time()
            print(mchoice, MapV, Objectivo, Verba)

            RaiosLst = GeraRaiosProt(Verba)

            for RaiosTuple in RaiosLst:
                if not RaiosTuple:  # Salta vazios
                    continue

                # Converte raios em inteiros
                raios = tuple(map(int, RaiosTuple))

                for raio in raios:
                    centro_row = raio
                    centro_col = raio
                    if (centro_row, centro_col, raio) in ZoneCenters:
                        centro_row = len(Zona) - raio -1
                        centro_col = raio
                    if (centro_row, centro_col, raio) in ZoneCenters:
                        centro_row = raio
                        centro_col = len(Zona[-1]) - raio -1
                    if (centro_row, centro_col, raio) in ZoneCenters:
                        centro_row = len(Zona) - raio -1
                        centro_col = len(Zona[-1]) - raio -1
                    while (centro_row, centro_col, raio) in ZoneCenters:
                        # Verifica o resto das colisoes e ajusta centro para +1+1 diagonal
                        if centro_col + 1 < len(Zona[0]):
                            centro_col += 1
                        else:
                            centro_row += 1
                            centro_col = raio
                    ZoneCenters.append((centro_row, centro_col, raio))

                # ProcuraCegaLargura para cada RaiosTuple
                solution, total_sum, Generations, Expansions = ProcuraCegaLargura(Zona, Objectivo, ZoneCenters, Generations, Expansions)

                if solution:
                    PrintFinalZona(Zona, Objectivo, solution, total_sum, Generations, Expansions, (mchoice, MapV))
                    break
                ZoneCenters = []  # Reset ZoneCenters for the next RaiosTuple

            ZoneCenters = []  # Reset ZoneCenters for the next RaiosTuple
            total_sum = 0
            Generations = 0
            Expansions = 0
            end_time = time.time()
            execution_time = end_time - start_time
            minutes = int(execution_time // 60)
            seconds = int(execution_time % 60)
            print("Tempo exec: {} min(s) e {} seg(s)".format(minutes, seconds))

            if not solution:
                print("***NO SOLUTION FOUND.***")

        elif choice == '3':
            print("\033[H\033[J", end="")  # clear screen
            for i, Zona in enumerate(LstZones):
                MapV = 'A'
                mchoice = i
                Zona = LstZones[mchoice]
                mchoice = str(mchoice + 1)
                print("\n", '-' * 80)
                current_time = time.localtime()
                print(f"Current time: {time.strftime('%H:%M:%S', current_time)}")

                Verba = params[mchoice]['Verba']
                Objectivo = params[mchoice][MapV]
                start_time = time.time()
                print(mchoice, MapV, Objectivo, Verba)

                RaiosLst = GeraRaiosProt(Verba)

                for RaiosTuple in RaiosLst:
                    if not RaiosTuple:  # Salta vazios
                        continue

                    # Converte raios em inteiros
                    raios = tuple(map(int, RaiosTuple))

                    for raio in raios:
                        centro_row = raio
                        centro_col = raio
                        if (centro_row, centro_col, raio) in ZoneCenters:
                            centro_row = len(Zona) - raio -1
                            centro_col = raio
                        if (centro_row, centro_col, raio) in ZoneCenters:
                            centro_row = raio
                            centro_col = len(Zona[-1]) - raio -1
                        if (centro_row, centro_col, raio) in ZoneCenters:
                            centro_row = len(Zona) - raio -1
                            centro_col = len(Zona[-1]) - raio -1
                        while (centro_row, centro_col, raio) in ZoneCenters:
                            # Verifica o resto das colisoes e ajusta centro para +1+1 diagonal
                            if centro_col + 1 < len(Zona[0]):
                                centro_col += 1
                            else:
                                centro_row += 1
                                centro_col = raio
                        ZoneCenters.append((centro_row, centro_col, raio))

                    # ProcuraCegaLargura para cada RaiosTuple
                    solution, total_sum, Generations, Expansions = ProcuraCegaLargura(Zona, Objectivo, ZoneCenters, Generations, Expansions)

                    if solution:
                        PrintFinalZona(Zona, Objectivo, solution, total_sum, Generations, Expansions, (mchoice, MapV))
                        break
                    ZoneCenters = []  # Reset ZoneCenters for the next RaiosTuple

                ZoneCenters = []  # Reset ZoneCenters for the next RaiosTuple
                total_sum = 0
                Generations = 0
                Expansions = 0
                end_time = time.time()
                execution_time = end_time - start_time
                minutes = int(execution_time // 60)
                seconds = int(execution_time % 60)
                print("Tempo exec: {} min(s) e {} seg(s)".format(minutes, seconds))

                if not solution:
                    print("***NO SOLUTION FOUND.***")

                MapV = 'B'
                mchoice = i
                Zona = LstZones[mchoice]
                mchoice = str(mchoice + 1)
                print("\n", '-' * 80)
                current_time = time.localtime()
                print(f"Current time: {time.strftime('%H:%M:%S', current_time)}")

                Verba = params[mchoice]['Verba']
                Objectivo = params[mchoice][MapV]
                start_time = time.time()
                print(mchoice, MapV, Objectivo, Verba)

                RaiosLst = GeraRaiosProt(Verba)

                for RaiosTuple in RaiosLst:
                    if not RaiosTuple:  # Salta vazios
                        continue

                    # Converte raios em inteiros
                    raios = tuple(map(int, RaiosTuple))

                    for raio in raios:
                        centro_row = raio
                        centro_col = raio
                        if (centro_row, centro_col, raio) in ZoneCenters:
                            centro_row = len(Zona) - raio -1
                            centro_col = raio
                        if (centro_row, centro_col, raio) in ZoneCenters:
                            centro_row = raio
                            centro_col = len(Zona[-1]) - raio -1
                        if (centro_row, centro_col, raio) in ZoneCenters:
                            centro_row = len(Zona) - raio -1
                            centro_col = len(Zona[-1]) - raio -1
                        while (centro_row, centro_col, raio) in ZoneCenters:
                            # Verifica o resto das colisoes e ajusta centro para +1+1 diagonal
                            if centro_col + 1 < len(Zona[0]):
                                centro_col += 1
                            else:
                                centro_row += 1
                                centro_col = raio
                        ZoneCenters.append((centro_row, centro_col, raio))

                    # ProcuraCegaLargura para cada RaiosTuple
                    solution, total_sum, Generations, Expansions = ProcuraCegaLargura(Zona, Objectivo, ZoneCenters, Generations, Expansions)

                    if solution:
                        PrintFinalZona(Zona, Objectivo, solution, total_sum, Generations, Expansions, (mchoice, MapV))
                        break
                    ZoneCenters = []  # Reset ZoneCenters for the next RaiosTuple

                ZoneCenters = []  # Reset ZoneCenters for the next RaiosTuple
                total_sum = 0
                Generations = 0
                Expansions = 0
                end_time = time.time()
                execution_time = end_time - start_time
                minutes = int(execution_time // 60)
                seconds = int(execution_time % 60)
                print("Tempo exec: {} min(s) e {} seg(s)".format(minutes, seconds))

                if not solution:
                    print("***NO SOLUTION FOUND.***")

                    print("\n\n")
        elif choice == 'q':
            print("Exiting the program...")
            return
        else:
            print("Invalid choice. Please try again.")


if __name__ == '__main__':
    main()