from gym_sgw.envs.enums.Enums import Actions, Terrains, MapObjects, Orientations, Modes


def next_action(observation, gamemode, mode):
    grid, status = observation

    x, y = status['player_location']
    energy = status['energy_remaining']
    turns = status['turns_executed']
    row = status['grid_rows']
    col = status['grid_cols']

    num_bat = 0

    for i in range(row):
        for j in range(col):
            if MapObjects.battery in grid[i][j].objects:
                num_bat += 1

    if energy < 25 + turns / 10 and num_bat > 0:
        return bfs(observation, MapObjects.battery, Modes.normal_mode)

    if gamemode == 1:
        if MapObjects.injured in grid[x][y].objects:
            return bfs(observation, Terrains.hospital, mode)
        else:
            return bfs(observation, MapObjects.injured, mode)
    else:
        return bfs(observation, None, mode)


def bfs(observation, target, mode):
    print("Target: " + str(target))
    queue = []
    queue2 = []
    grid, status = observation

    x, y = status['player_location']

    row = status['grid_rows']
    col = status['grid_cols']

    vis = [[False for _ in range(row)] for _ in range(col)]

    orientation = status['player_orientation']

    orientations = [Orientations.up, Orientations.right, Orientations.down, Orientations.left]
    objects = [MapObjects.injured, MapObjects.zombie, MapObjects.battery]

    dx = [-1, 0, 1, 0]
    dy = [0, 1, 0, -1]

    # actions = [Actions.step_forward, Actions.turn_left, Actions.turn_right]

    queue.append((-1, x, y))
    vis[x][y] = True

    selected = 0

    while len(queue) > 0 or len(queue2) > 0:  # BFS time
        if len(queue) == 0:
            for x, y, z in queue2:
                queue.append((x, y, z))
                queue2.pop(0)

        curf, curx, cury = queue.pop(0)

        if target:
            if target in objects:
                if target in grid[curx][cury].objects:
                    # print(str(curx) + " " + str(cury))
                    selected = curf
                    break
            else:
                if grid[curx][cury].terrain in [target]:
                    selected = curf
                    break
        else:
            if curx == x and cury == y:
                pass
            elif MapObjects.injured in grid[curx][cury].objects or MapObjects.pedestrian in grid[curx][
                cury].objects or MapObjects.zombie in grid[curx][cury].objects or MapObjects.battery in grid[curx][
                cury].objects:
                selected = curf
                break

        for i in range(4):
            nx = curx + dx[i]
            ny = cury + dy[i]
            newf = curf

            if grid[nx][ny].terrain in [Terrains.wall, Terrains.none, Terrains.out_of_bounds]:
                continue

            if vis[nx][ny]:
                continue

            if newf == -1:
                newf = i

            add = False

            if target:
                if mode == Modes.zombie_mode:
                    if MapObjects.zombie in grid[nx][ny].objects:
                        queue.insert(0, (newf, nx, ny))
                        add = True

            if target:
                if not add:
                    if MapObjects.pedestrian in grid[nx][ny].objects:
                        queue2.append((newf, nx, ny))
                    elif grid[nx][ny].terrain in [Terrains.mud, Terrains.fire]:
                        queue2.append((newf, nx, ny))
                    else:
                        if target != MapObjects.injured:
                            if MapObjects.injured in grid[nx][ny].objects:
                                queue2.append((newf, nx, ny))
                            else:
                                queue.append((newf, nx, ny))
                        else:
                            queue.append((newf, nx, ny))
            else:
                queue.append((newf, nx, ny))

            vis[nx][ny] = True

    idx = 0
    for i in range(4):
        if orientation == orientations[i]:
            idx = i
            break

    dist1 = 0
    dist2 = 0
    temp = idx

    if orientation == orientations[selected]:
        return Actions.step_forward

    for i in range(4):
        if orientations[idx] == orientations[selected]:
            break
        dist1 += 1
        idx += 1
        idx %= 4

    idx = temp

    for i in range(4):
        if orientations[idx] == orientations[selected]:
            break
        dist2 += 1
        idx -= 1
        idx %= 4

    # print(str(dist1) + " " + str(dist2))

    if dist1 > dist2:
        return Actions.turn_left
    else:
        return Actions.turn_right