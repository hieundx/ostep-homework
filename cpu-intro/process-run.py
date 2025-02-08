#! /usr/bin/env python

from __future__ import print_function
import sys
from optparse import OptionParser
import random

# to make Python2 and Python3 act the same -- how dumb
def random_seed(seed):
    try:
        random.seed(seed, version=1)
    except:
        random.seed(seed)
    return

# process switch behavior
SCHED_SWITCH_ON_IO = 'SWITCH_ON_IO' # run other ready processes when an IO is issued
SCHED_SWITCH_ON_END = 'SWITCH_ON_END' # wait until current process's IO is done

# io finished behavior
IO_RUN_LATER = 'IO_RUN_LATER' # run other processes after IO is done
IO_RUN_IMMEDIATE = 'IO_RUN_IMMEDIATE' # run the next instruction in the current process after IO is done

# process states
STATE_RUNNING = 'RUNNING'
STATE_READY = 'READY'
STATE_DONE = 'DONE'
STATE_WAIT = 'BLOCKED'

# members of process structure
PROC_CODE = 'code_'
PROC_PC = 'pc_'
PROC_ID = 'pid_'
PROC_STATE = 'proc_state_'

# things a process can do
DO_COMPUTE = 'cpu'
DO_IO = 'io'
DO_IO_DONE = 'io_done'

class scheduler:
  
    def __init__(self, process_switch_behavior, io_done_behavior, io_length):
        """
        Initializes the ProcessRun object.

        Args:
            process_switch_behavior (str): The behavior of the process switch. Default: SWITCH_ON_IO.
            io_done_behavior (str): The behavior when I/O is done. Default: IO_RUN_LATER.
            io_length (int): The length of the I/O operation. Default: 5.

        Attributes:
            proc_info (dict): A dictionary to keep the set of instructions for each of the processes.
            process_switch_behavior (str): The behavior of the process switch.
            io_done_behavior (str): The behavior when I/O is done.
            io_length (int): The length of the I/O operation.
        """
        # keep set of instructions for each of the processes
    
        self.proc_info = {}
        self.process_switch_behavior = process_switch_behavior
        self.io_done_behavior = io_done_behavior
        self.io_length = io_length
        return

    def new_process(self):
        # proc_id is 0-indexed, so the next one is the length of the dictionary
        proc_id = len(self.proc_info)
        """
        Example:
        {
            0: {
                'pc_': 1,                       # program counter has advanced to index 1
                'pid_': 0,                      # process id is 0
                'code_': ['cpu', 'io', 'io_done', 'cpu'],  # list of instructions remaining/loaded
                'proc_state_': 'RUNNING'        # current state is running
            },
            1: {
                'pc_': 0,                       # process counter is at the beginning
                'pid_': 1,                      # process id is 1
                'code_': ['cpu', 'cpu'],         # list of instructions loaded
                'proc_state_': 'READY'          # state is ready but not yet running
            }
        }
        """
        self.proc_info[proc_id] = {}
        self.proc_info[proc_id][PROC_PC] = 0 # Unused, but why?
        self.proc_info[proc_id][PROC_ID] = proc_id
        self.proc_info[proc_id][PROC_CODE] = []
        self.proc_info[proc_id][PROC_STATE] = STATE_READY
        return proc_id

    def load_program(self, program):
        """
        Loads a program into the process's instruction set.
        The program is a string where each instruction is separated by a comma.
        Each instruction starts with an opcode ('c' for compute or 'i' for I/O)
        followed by a number indicating the duration or count.
        Args:
            program (str): A string representing the program instructions.
                   Example: 'c5,i,c3' where 'c5' means compute for 5 cycles,
                   'i' means perform I/O, and 'c3' means compute for 3 cycles.
                   IO duration is defined by the self.io_length attribute.
        Returns:
            None
        """
        
        proc_id = self.new_process()
        for line in program.split(','):
            opcode = line[0] # opcode, e.g. 'c5' -> 'c', 'i' -> 'i'
            
            if opcode == 'c': # compute
                num = int(line[1:]) # second character onwards is the duration, e.g. 'c5' -> 5
                for i in range(num): # add `num` compute instructions to the process
                    self.proc_info[proc_id][PROC_CODE].append(DO_COMPUTE)
            elif opcode == 'i': # I/O
                self.proc_info[proc_id][PROC_CODE].append(DO_IO) # add an I/O instruction
                self.proc_info[proc_id][PROC_CODE].append(DO_IO_DONE)
            else:
                print('bad opcode %s (should be c or i)' % opcode)
                exit(1)
        return

    def load(self, program_description):
        """
        Load a program into the process table.
        Args:
            program_description (str): A string describing the program in the format 'X:Y',
                                       where X is the number of instructions and Y is the 
                                       percent chance that an instruction is CPU-bound (as opposed to IO-bound).
        Raises:
            SystemExit: If the program description is not in the correct format.
        Returns:
            None
        """
        
        proc_id = self.new_process()
        tmp = program_description.split(':')
        if len(tmp) != 2:
            print('Bad description (%s): Must be number <x:y>' % program_description)
            print('  where X is the number of instructions')
            print('  and Y is the percent change that an instruction is CPU not IO')
            exit(1)

        num_instructions, chance_cpu = int(tmp[0]), float(tmp[1])/100.0
        
        # Add cpu or io instructions based on the chance_cpu
        for i in range(num_instructions):
            if random.random() < chance_cpu:
                self.proc_info[proc_id][PROC_CODE].append(DO_COMPUTE)
            else:
                self.proc_info[proc_id][PROC_CODE].append(DO_IO)
                # add one compute to HANDLE the I/O completion
                self.proc_info[proc_id][PROC_CODE].append(DO_IO_DONE)
        return

    def move_to_ready(self, expected, pid=-1):
        if pid == -1:
            pid = self.curr_proc
        assert(self.proc_info[pid][PROC_STATE] == expected)
        self.proc_info[pid][PROC_STATE] = STATE_READY
        return

    def move_to_wait(self, expected):
        assert(self.proc_info[self.curr_proc][PROC_STATE] == expected)
        self.proc_info[self.curr_proc][PROC_STATE] = STATE_WAIT
        return

    def move_to_running(self, expected):
        assert(self.proc_info[self.curr_proc][PROC_STATE] == expected)
        self.proc_info[self.curr_proc][PROC_STATE] = STATE_RUNNING
        return

    def move_to_done(self, expected):
        assert(self.proc_info[self.curr_proc][PROC_STATE] == expected)
        self.proc_info[self.curr_proc][PROC_STATE] = STATE_DONE
        return


    def next_proc(self, pid=-1):
        """
        Move to the next process and set its state from ready to running.
        """
        
        # if pid is not provided, use the current process
        if pid != -1:
            self.curr_proc = pid
            self.move_to_running(STATE_READY)
            return
        
        # if pid is not provided, find the first process in the ready state in a circular manner
        # 1st loop looks for the next process in the list
        for pid in range(self.curr_proc + 1, len(self.proc_info)):
            if self.proc_info[pid][PROC_STATE] == STATE_READY:
                self.curr_proc = pid
                self.move_to_running(STATE_READY)
                return
        # 2nd loop looks for the process from the beginning of the list
        for pid in range(0, self.curr_proc + 1):
            if self.proc_info[pid][PROC_STATE] == STATE_READY:
                self.curr_proc = pid
                self.move_to_running(STATE_READY)
                return
        return

    def get_num_processes(self):
        return len(self.proc_info)

    def get_num_instructions(self, pid):
        return len(self.proc_info[pid][PROC_CODE])

    def get_instruction(self, pid, index):
        return self.proc_info[pid][PROC_CODE][index]

    def get_num_active(self):
        num_active = 0
        for pid in range(len(self.proc_info)):
            if self.proc_info[pid][PROC_STATE] != STATE_DONE:
                num_active += 1
        return num_active

    def get_num_runnable(self):
        num_active = 0
        for pid in range(len(self.proc_info)):
            if self.proc_info[pid][PROC_STATE] == STATE_READY or \
                   self.proc_info[pid][PROC_STATE] == STATE_RUNNING:
                num_active += 1
        return num_active

    def get_ios_in_flight(self, current_time):
        """
            Returns the number of IOs in flight at the current time.
            current_time (int): The current clock tick.
            
            Loop through all processes and check if current time is before the IO finish time.
            If it is, increment the number of IOs in flight.
        """
        
        num_in_flight = 0
        for pid in range(len(self.proc_info)):
            for t in self.io_finish_times[pid]: 
                if t > current_time:
                    num_in_flight += 1
        return num_in_flight

    def check_for_switch(self):
        return

    def space(self, num_columns):
        for i in range(num_columns):
            print('%10s' % ' ', end='')

    def check_if_done(self):
        if len(self.proc_info[self.curr_proc][PROC_CODE]) == 0:
            if self.proc_info[self.curr_proc][PROC_STATE] == STATE_RUNNING:
                self.move_to_done(STATE_RUNNING)
                self.next_proc()
        return

    def run(self):
        clock_tick = 0

        if len(self.proc_info) == 0:
            return

        # track outstanding IOs, per process
        self.io_finish_times = {}
        for pid in range(len(self.proc_info)):
            self.io_finish_times[pid] = []

        # make first one active
        self.curr_proc = 0
        self.move_to_running(STATE_READY)

        # OUTPUT: headers for each column
        print('%s' % 'Time', end='') 
        for pid in range(len(self.proc_info)):
            print('%14s' % ('PID:%2d' % (pid)), end='')
        print('%14s' % 'CPU', end='')
        print('%14s' % 'IOs', end='')
        print('')

        # init statistics
        io_busy = 0
        cpu_busy = 0

        while self.get_num_active() > 0:
            clock_tick += 1

            # check for io finish
            io_done = False
            for pid in range(len(self.proc_info)):
                if clock_tick in self.io_finish_times[pid]:
                    io_done = True
                    self.move_to_ready(STATE_WAIT, pid)
                    if self.io_done_behavior == IO_RUN_IMMEDIATE:
                        # IO_RUN_IMMEDIATE
                        # This means that an IO has finished and that process wants to handle the IO completion immediately
                        # so we pause the current process and switch to the process that issued the IO
                        if self.curr_proc != pid:
                            if self.proc_info[self.curr_proc][PROC_STATE] == STATE_RUNNING:
                                self.move_to_ready(STATE_RUNNING)
                        self.next_proc(pid)
                    else:
                        # IO_RUN_LATER
                        if self.process_switch_behavior == SCHED_SWITCH_ON_END and self.get_num_runnable() > 1:
                            # this means the process that issued the io should be run
                            self.next_proc(pid)
                        if self.get_num_runnable() == 1:
                            # this is the only thing to run: so run it
                            self.next_proc(pid)
                    self.check_if_done()
            
            # if current proc is RUNNING and has an instruction, execute it
            instruction_to_execute = ''
            if self.proc_info[self.curr_proc][PROC_STATE] == STATE_RUNNING and \
                   len(self.proc_info[self.curr_proc][PROC_CODE]) > 0:
                instruction_to_execute = self.proc_info[self.curr_proc][PROC_CODE].pop(0)
                cpu_busy += 1

            # OUTPUT: print what everyone is up to
            if io_done:
                print('%3d*' % clock_tick, end='')
            else:
                print('%3d ' % clock_tick, end='')
            for pid in range(len(self.proc_info)):
                if pid == self.curr_proc and instruction_to_execute != '':
                    print('%14s' % ('RUN:'+instruction_to_execute), end='')
                else:
                    print('%14s' % (self.proc_info[pid][PROC_STATE]), end='')

            # CPU output here: if no instruction executes, output a space, otherwise a 1 
            if instruction_to_execute == '':
                print('%14s' % ' ', end='')
            else:
                print('%14s' % '1', end='')

            # IO output here:
            num_outstanding = self.get_ios_in_flight(clock_tick)
            if num_outstanding > 0:
                print('%14s' % str(num_outstanding), end='')
                io_busy += 1
            else:
                print('%10s' % ' ', end='')
            print('')

            # if this is an IO start instruction, switch to waiting state
            # and add an io completion in the future
            if instruction_to_execute == DO_IO:
                self.move_to_wait(STATE_RUNNING)
                self.io_finish_times[self.curr_proc].append(clock_tick + self.io_length + 1)
                if self.process_switch_behavior == SCHED_SWITCH_ON_IO:
                    self.next_proc()

            # ENDCASE: check if currently running thing is out of instructions
            self.check_if_done()
        return (cpu_busy, io_busy, clock_tick)
        
#
# PARSE ARGUMENTS
#

parser = OptionParser()
parser.add_option('-s', '--seed', default=0, help='the random seed', action='store', type='int', dest='seed')
parser.add_option('-P', '--program', default='', help='more specific controls over programs', action='store', type='string', dest='program')
parser.add_option('-l', '--processlist', default='', help='a comma-separated list of processes to run, in the form X1:Y1,X2:Y2,... where X is the number of instructions that process should run, and Y the chances (from 0 to 100) that an instruction will use the CPU or issue an IO (i.e., if Y is 100, a process will ONLY use the CPU and issue no I/Os; if Y is 0, a process will only issue I/Os)', action='store', type='string', dest='process_list')
parser.add_option('-L', '--iolength', default=5, help='how long an IO takes', action='store', type='int', dest='io_length')
parser.add_option('-S', '--switch', default='SWITCH_ON_IO', help='when to switch between processes: SWITCH_ON_IO, SWITCH_ON_END', action='store', type='string', dest='process_switch_behavior')
parser.add_option('-I', '--iodone', default='IO_RUN_LATER', help='type of behavior when IO ends: IO_RUN_LATER, IO_RUN_IMMEDIATE', action='store', type='string', dest='io_done_behavior')
parser.add_option('-c', help='compute answers for me', action='store_true', default=False, dest='solve')
parser.add_option('-p', '--printstats', help='print statistics at end; only useful with -c flag (otherwise stats are not printed)', action='store_true', default=False, dest='print_stats')
(options, args) = parser.parse_args()

random_seed(options.seed)

assert(options.process_switch_behavior == SCHED_SWITCH_ON_IO or options.process_switch_behavior == SCHED_SWITCH_ON_END)
assert(options.io_done_behavior == IO_RUN_IMMEDIATE or options.io_done_behavior == IO_RUN_LATER)

s = scheduler(options.process_switch_behavior, options.io_done_behavior, options.io_length)

if options.program != '':
    for p in options.program.split(':'):
        s.load_program(p)
else:
    # example process description (10:100,10:100)
    for p in options.process_list.split(','):
        s.load(p)

assert(options.io_length >= 0)

if options.solve == False:
    print('Produce a trace of what would happen when you run these processes:')
    for pid in range(s.get_num_processes()):
        print('Process %d' % pid)
        for inst in range(s.get_num_instructions(pid)):
            print('  %s' % s.get_instruction(pid, inst))
        print('')
    print('Important behaviors:')
    print('  System will switch when ', end='')
    if options.process_switch_behavior == SCHED_SWITCH_ON_IO:
        print('the current process is FINISHED or ISSUES AN IO')
    else:
        print('the current process is FINISHED')
    print('  After IOs, the process issuing the IO will ', end='')
    if options.io_done_behavior == IO_RUN_IMMEDIATE:
        print('run IMMEDIATELY')
    else:
        print('run LATER (when it is its turn)')
    print('')
    exit(0)

(cpu_busy, io_busy, clock_tick) = s.run()

if options.print_stats:
    print('')
    print('Stats: Total Time %d' % clock_tick)
    print('Stats: CPU Busy %d (%.2f%%)' % (cpu_busy, 100.0 * float(cpu_busy)/clock_tick))
    print('Stats: IO Busy  %d (%.2f%%)' % (io_busy, 100.0 * float(io_busy)/clock_tick))
    print('')
