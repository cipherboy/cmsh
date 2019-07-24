/*
 * Python bindings for cmsh's native interface.
 *
 * Copyright (C) 2019 Alexander Scheel <alexander.m.scheel@gmail.com>
 *
 * See LICENSE in the root of the repository for license information.
 *
 * https://github.com/cipherboy/cmsh
 * High level bindings for Mate Soos's CryptoMiniSat.
 */

#include <cstdint>
#include <cfloat>
#include <Python.h>
#include "cmsh.h"

using namespace cmsh;

// Validate the internal state of the native_model object: self should never
// be NULL and self->model should not be NULL when the instance is
// initialized. If either of these don't hold, raise an exception telling the
// user to initialize the instance first; this prevents an ugly segfault like
// pycryptosat has had.
#define check_null \
    if (self == NULL || self->model == NULL) { \
        PyErr_SetString(PyExc_ValueError, "Error! You need to initialize (with __init__) the native model before calling this function."); \
    }

// A common implementation for functions which return a value. This lets us
// implement it once here and reuse the macro everywhere.
#define get_int_value(v_method) \
    check_null \
    int result = self->model->v_method(); \
    return PyLong_FromLong(result);

// A v_op method common implementation. This lets us implement it once (here)
// and use the macro everywhere. Left and right are keyword arguments, though
// really need not be.
#define v_op(v_method) \
    char *kwlist[] = {(char*)"left", (char *)"right", NULL}; \
    int left = 0; \
    int right = 0; \
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "ii", kwlist, &left, &right)) { \
        return NULL; \
    } \
    check_null \
    int result = self->model->v_method(left, right); \
    return PyLong_FromLong(result);


// PyObject definition for wrapping the cmsh native interface.
typedef struct {
    // Become a PyObject struct... :)
    PyObject_HEAD

    /* Members for cmsh's native bindings: a pointer to a model_t instance */
    model_t *model;
} native_model;


PyDoc_STRVAR(config_timeout_doc,
    "void config_timeout(double max_time)\n\n"
    "Set the maximum time in seconds that the solver should run for, for\n"
    "any given call to SATSolver->solve(). Note that you can call\n"
    "SATSolver->solve() multiple times with different assumptions and\n"
    "different timeouts/conflict counts if you desire.\n\n"
    "Parameters\n"
    "----------\n"
    "max_time : float\n"
    "    maximum time limit to solve for\n"
);

static PyObject *config_timeout(native_model *self, PyObject *args, PyObject *kwds) {
    static char *kwlist[] = {(char *)"max_time", NULL};
    double max_time = DBL_MAX;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "d", kwlist, &max_time)) {
        return NULL;
    }

    check_null

    self->model->config_timeout(max_time);
    Py_RETURN_NONE;
}


PyDoc_STRVAR(config_conflicts_doc,
    "void config_conflicts(int64_t max_conflicts)\n\n"
    "Configure the maximum number of conflicts until the solver should\n"
    "exit on any given call to SATSolver->solve(). See note on\n"
    "config_timeout(...) as well.\n\n"
    "Parameters\n"
    "----------\n"
    "max_conflicts : int\n"
    "    maximum number of conflicts to solve for\n"
);

static PyObject *config_conflicts(native_model *self, PyObject *args, PyObject *kwds) {
    char *kwlist[] {(char *)"max_conflicts", NULL};
    int64_t max_conflicts = LLONG_MAX;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "L", kwlist, &max_conflicts)) {
        return NULL;
    }

    check_null

    self->model->config_conflicts(max_conflicts);
    Py_RETURN_NONE;
}


PyDoc_STRVAR(var_doc,
    "int var()\n\n"
    "Create a new constraint variable, returning its value. This should be\n"
    "used with all calls below; the value from cnf(...) should never be\n"
    "ysed unless parsing the generated CNF and correlating the variables\n"
    "there with constraint variables. However, cmsh takes care of this for\n"
    "the caller.\n\n"
    "Returns\n"
    "-------\n"
    "int\n"
    "    the next available constraint variable identifier\n"
);

static PyObject *var(native_model *self, PyObject *) {
    get_int_value(var);
}


PyDoc_STRVAR(cnf_doc,
    "int cnf(int var)\n\n"
    "Inquire as to the value of the cnf variable for the associated\n"
    "constraint variable. Returns 0 when the constraint variable hasn't\n"
    "yet been assigned a CNF counterpart. Note that this value shouldn't be\n"
    "passed to any other methods in cmsh's API unless otherwise noted.\n\n"
    "Parameters\n"
    "----------\n"
    "var : int\n"
    "    The identifier of a constraint variable\n\n"
    "Returns\n"
    "-------\n"
    "int\n"
    "    The (non-zero) identifier of the corresponding CNF variable, else\n"
    "    zero if one is not yet assigned.\n"
);

static PyObject *cnf(native_model *self, PyObject *args, PyObject *kwds) {
    char *kwlist[] = {(char*)"var", NULL};
    int constraint_var = 0;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "i", kwlist, &constraint_var)) {
        return NULL;
    }

    check_null

    int cnf_variable = self->model->cnf(constraint_var);
    return PyLong_FromLong(cnf_variable);
}


PyDoc_STRVAR(v_and_doc,
    "int v_and(int left, int right)\n\n"
    "Create a new AND gate over the two constraint variables and add it\n"
    "to the model. The result is another constraint variable which\n"
    "represents the value of the gate, and can be used in other gates.\n\n"
    "Parameters\n"
    "----------\n"
    "left : int\n"
    "    the identifier of a constraint variable\n"
    "right : int\n"
    "    the identifier of a constraint variable\n\n"
    "Returns\n"
    "-------\n"
    "int\n"
    "    The identifier of the constraint variable associated with the value\n"
    "    of this gate.\n"
);

static PyObject *v_and(native_model *self, PyObject *args, PyObject *kwds) {
    v_op(v_and)
}


PyDoc_STRVAR(v_nand_doc,
    "int v_nand(int left, int right)\n\n"
    "Create a new NAND gate over the two constraint variables and add it\n"
    "to the model. The result is another constraint variable which\n"
    "represents the value of the gate, and can be used in other gates.\n\n"
    "Parameters\n"
    "----------\n"
    "left : int\n"
    "    the identifier of a constraint variable\n"
    "right : int\n"
    "    the identifier of a constraint variable\n\n"
    "Returns\n"
    "-------\n"
    "int\n"
    "    The identifier of the constraint variable associated with the value\n"
    "    of this gate.\n"
);

static PyObject *v_nand(native_model *self, PyObject *args, PyObject *kwds) {
    v_op(v_nand)
}


PyDoc_STRVAR(v_or_doc,
    "int v_or(int left, int right)\n\n"
    "Create a new OR gate over the two constraint variables and add it\n"
    "to the model. The result is another constraint variable which\n"
    "represents the value of the gate, and can be used in other gates.\n\n"
    "Parameters\n"
    "----------\n"
    "left : int\n"
    "    the identifier of a constraint variable\n"
    "right : int\n"
    "    the identifier of a constraint variable\n\n"
    "Returns\n"
    "-------\n"
    "int\n"
    "    The identifier of the constraint variable associated with the value\n"
    "    of this gate.\n"
);

static PyObject *v_or(native_model *self, PyObject *args, PyObject *kwds) {
    v_op(v_or)
}


PyDoc_STRVAR(v_nor_doc,
    "int v_nor(int left, int right)\n\n"
    "Create a new NOR gate over the two constraint variables and add it\n"
    "to the model. The result is another constraint variable which\n"
    "represents the value of the gate, and can be used in other gates.\n\n"
    "Parameters\n"
    "----------\n"
    "left : int\n"
    "    the identifier of a constraint variable\n"
    "right : int\n"
    "    the identifier of a constraint variable\n\n"
    "Returns\n"
    "-------\n"
    "int\n"
    "    The identifier of the constraint variable associated with the value\n"
    "    of this gate.\n"
);

static PyObject *v_nor(native_model *self, PyObject *args, PyObject *kwds) {
    v_op(v_nor)
}


PyDoc_STRVAR(v_xor_doc,
    "int v_xor(int left, int right)\n\n"
    "Create a new XOR gate over the two constraint variables and add it\n"
    "to the model. The result is another constraint variable which\n"
    "represents the value of the gate, and can be used in other gates.\n\n"
    "Parameters\n"
    "----------\n"
    "left : int\n"
    "    the identifier of a constraint variable\n"
    "right : int\n"
    "    the identifier of a constraint variable\n\n"
    "Returns\n"
    "-------\n"
    "int\n"
    "    The identifier of the constraint variable associated with the value\n"
    "    of this gate.\n"
);

static PyObject *v_xor(native_model *self, PyObject *args, PyObject *kwds) {
    v_op(v_xor)
}


PyDoc_STRVAR(v_assert_doc,
    "void v_assert(int var)\n\n"
    "Assert that a single constraint variable is true. A negative variable\n"
    "identifier can be passed here, in which case the negation of the\n"
    "variable is asserted to be true, i.e., the variable is asserted to be\n"
    "false. Note that assertions cannot be removed once added, unlike\n"
    "assumptions, which can be with assume(...)/unassume(...).\n\n"
    "Parameters\n"
    "----------\n"
    "var : int\n"
    "    the identifier of a constraint variable\n"
);

static PyObject *v_assert(native_model *self, PyObject *args, PyObject *kwds) {
    char *kwlist[] = {(char*)"var", NULL};
    int constraint_var = 0;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "i", kwlist, &constraint_var)) {
        return NULL;
    }

    check_null;

    self->model->v_assert(constraint_var);
    Py_RETURN_NONE;
}


PyDoc_STRVAR(v_assume_doc,
    "void v_assume(int var)\n\n"
    "Add an assumption about the state of a variable to the model. A\n"
    "negative assumption can be passed by making the identifier negative.\n\n"
    "Parameters\n"
    "----------\n"
    "var : int\n"
    "    the identifier of a constraint variable\n"
);

static PyObject *v_assume(native_model *self, PyObject *args, PyObject *kwds) {
    char *kwlist[] = {(char*)"var", NULL};
    int constraint_var = 0;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "i", kwlist, &constraint_var)) {
        return NULL;
    }

    check_null;

    self->model->v_assume(constraint_var);
    Py_RETURN_NONE;
}


PyDoc_STRVAR(v_unassume_doc,
    "void v_unassume(int var)\n\n"
    "Remove all assumptions about the state of a variable from the model.\n"
    "This removes both positive and negative assumptions; i.e., remove both\n"
    "assume(var) and assume(-var) at the same time.\n\n"
    "Parameters\n"
    "----------\n"
    "var : int\n"
    "    the identifier of a constraint variable\n"
);

static PyObject *v_unassume(native_model *self, PyObject *args, PyObject *kwds) {
    char *kwlist[] = {(char*)"var", NULL};
    int constraint_var = 0;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "i", kwlist, &constraint_var)) {
        return NULL;
    }

    check_null;

    self->model->v_unassume(constraint_var);
    Py_RETURN_NONE;
}


PyDoc_STRVAR(solve_doc,
    "lbool solve()\n\n"
    "Solve the model under the specified set of assumptions. The result is\n"
    "either True (if SAT), False (if UNSAT) or None (if neither SAT nor\n"
    "UNSAT have been reached yet, usually due to reaching a timeout or\n"
    "conflict limit.\n\n"
    "Returns\n"
    "-------\n"
    "bool\n"
    "    Whether or not the model is satisfiable\n"
);

static PyObject *solve(native_model *self, PyObject *args) {
    check_null;

    lbool ret = self->model->solve();
    if (ret == l_True) {
        Py_RETURN_TRUE;
    }

    if (ret == l_False) {
        Py_RETURN_FALSE;
    }

    Py_RETURN_NONE;
}


PyDoc_STRVAR(val_doc,
    "bool val(int var)\n\n"
    "Get the value of a constraint variable after solve returns l_True. If\n"
    "solve returns anything other than l_True and val(...) is called, it\n"
    "will assert.\n\n"
    "Parameters\n"
    "----------\n"
    "var : int\n"
    "    the identifier of a constraint variable\n\n"
    "Returns\n"
    "-------\n"
    "bool\n"
    "    The value of the constraint variable\n"
);

static PyObject *val(native_model *self, PyObject *args, PyObject *kwds) {
    char *kwlist[] = {(char*)"var", NULL};
    int constraint_var = 0;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "i", kwlist, &constraint_var)) {
        return NULL;
    }

    check_null;

    if (self->model->val(constraint_var)) {
        Py_RETURN_TRUE;
    }

    Py_RETURN_FALSE;
}


PyDoc_STRVAR(num_constraint_vars_doc,
    "int num_constraint_vars()\n\n"
    "Query the number of constraint variables in this model instance.\n\n"
    "Returns\n"
    "-------\n"
    "int\n"
    "    The number of constraint variables in the model\n"
);

static PyObject *num_constraint_vars(native_model *self, PyObject *) {
    get_int_value(num_constraint_vars);
}


PyDoc_STRVAR(num_constraints_doc,
    "int num_constraints()\n\n"
    "Query the number of constraints in this model instance.\n\n"
    "Returns\n"
    "-------\n"
    "int\n"
    "    The number of constraints in the model\n"
);

static PyObject *num_constraints(native_model *self, PyObject *) {
    get_int_value(num_constraints);
}


PyDoc_STRVAR(num_cnf_vars_doc,
    "int num_cnf_vars()\n\n"
    "Query the number of CNF variables in this model instance.\n\n"
    "Returns\n"
    "-------\n"
    "int\n"
    "    The number of CNF variables in the model\n"
);

static PyObject *num_cnf_vars(native_model *self, PyObject *) {
    get_int_value(num_cnf_vars);
}


PyDoc_STRVAR(num_cnf_clauses_doc,
    "int num_cnf_clauses()\n\n"
    "Query the number of CNF clauses in this model instance.\n\n"
    "Returns\n"
    "-------\n"
    "int\n"
    "    The number of CNF clauses in the model\n"
);

static PyObject *num_cnf_clauses(native_model *self, PyObject *) {
    get_int_value(num_cnf_clauses);
}


PyDoc_STRVAR(delete_model_doc,
    "void delete_model()\n\n"
    "Delete the underlying model instance, freeing memory. This should only\n"
    "be used when waiting for garbage collection on large models isn't\n"
    "possible.\n"
);

static PyObject *delete_model(native_model *self, PyObject *) {
    check_null

    delete self->model;
    self->model = NULL;
    Py_RETURN_NONE;
}


static int model_init(native_model *self, PyObject *args, PyObject *kwds) {
    char *kwlist[] = {(char *)"threads", (char *)"gauss", NULL};
    int threads = 1;
    bool gauss = true;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|ip", kwlist, &threads, &gauss)) {
        return -1;
    }

    if (threads < 1) {
        threads = 1;
    }

    if (self->model != NULL) {
        delete self->model;
    }

    self->model = new model_t(threads, gauss);
    if (!self->model) {
        return -1;
    }

    return 0;
}

static void model_dealloc(native_model *ptr) {
    if (ptr != NULL && ptr->model != NULL) {
        delete ptr->model;
    }
}

static PyMethodDef model_methods[] = {
    {"config_timeout", (PyCFunction)config_timeout, METH_VARARGS | METH_KEYWORDS, config_timeout_doc},
    {"config_conflicts", (PyCFunction)config_conflicts, METH_VARARGS | METH_KEYWORDS, config_conflicts_doc},
    {"var", (PyCFunction)var, METH_VARARGS, var_doc},
    {"cnf", (PyCFunction)cnf, METH_VARARGS | METH_KEYWORDS, cnf_doc},
    {"v_and", (PyCFunction)v_and, METH_VARARGS | METH_KEYWORDS, v_and_doc},
    {"v_nand", (PyCFunction)v_nand, METH_VARARGS | METH_KEYWORDS, v_nand_doc},
    {"v_or", (PyCFunction)v_or, METH_VARARGS | METH_KEYWORDS, v_or_doc},
    {"v_nor", (PyCFunction)v_nor, METH_VARARGS | METH_KEYWORDS, v_nor_doc},
    {"v_xor", (PyCFunction)v_xor, METH_VARARGS | METH_KEYWORDS, v_xor_doc},
    {"v_assert", (PyCFunction)v_assert, METH_VARARGS | METH_KEYWORDS, v_assert_doc},
    {"v_assume", (PyCFunction)v_assume, METH_VARARGS | METH_KEYWORDS, v_assume_doc},
    {"v_unassume", (PyCFunction)v_unassume, METH_VARARGS | METH_KEYWORDS, v_unassume_doc},
    {"solve", (PyCFunction)solve, METH_VARARGS, solve_doc},
    {"val", (PyCFunction)val, METH_VARARGS | METH_KEYWORDS, val_doc},
    {"num_constraint_vars", (PyCFunction)num_constraint_vars, METH_VARARGS, num_constraint_vars_doc},
    {"num_constraints", (PyCFunction)num_constraints, METH_VARARGS, num_constraints_doc},
    {"num_cnf_vars", (PyCFunction)num_cnf_vars, METH_VARARGS, num_cnf_vars_doc},
    {"num_cnf_clauses", (PyCFunction)num_cnf_clauses, METH_VARARGS, num_cnf_clauses_doc},
    {"delete_model", (PyCFunction)delete_model, METH_VARARGS, delete_model_doc},
    {NULL, NULL, 0, NULL},
};

static PyTypeObject native_model_type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "cmsh._native.model",   // tp_name
    sizeof(native_model),   // tp_basicsize
    0, // tp_itemsize -- zero, since we don't increase in size based on the
       // number of elements we hold
    (destructor) model_dealloc, // tp_dealloc
    0, // tp_print
    0, // tp_getattr
    0, // tp_setattr
    0, // tp_as_async
    0, // tp_repr
    0, // tp_as_number
    0, // tp_as_sequence
    0, // tp_as_mapping
    0, // tp_hash
    0, // tp_call
    0, // tp_str
    0, // tp_getattro
    0, // tp_setattro
    0, // tp_as_buffer
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, // tp_flags
    0, // tp_doc
    0, // tp_traverse
    0, // tp_clear
    0, // tp_richcompare
    0, // tp_weaklistoffset
    0, // tp_iter
    0, // tp_iternext
    model_methods, // tp_methods
    0, // tp_members
    0, // tp_getset
    0, // tp_base
    0, // tp_dict
    0, // tp_descr_get
    0, // tp_descr_set
    0, // tp_dictoffset
    (initproc)model_init, // tp_init
    0, // tp_alloc
    &PyType_GenericNew, // tp_new
};

/*
 * pycmsh
 */
static struct PyModuleDef native_def = {
    PyModuleDef_HEAD_INIT, // m_base
    "cmsh._native", // m_name
    "Python bindings for cmsh's native interface.", // m_doc
    -1, // m_size
    NULL, // m_methods
    NULL, // m_reload
    NULL, // m_traverse
    NULL, // m_clear
    NULL, // m_free
};

PyMODINIT_FUNC PyInit__native(void) {
    PyObject *module;

    // Create our Python module, _cmsh. This hides the native definition from
    // most Python callers: they'll import cmsh and won't be bothered by the
    // details of the native bindings.
    //
    // See also: https://docs.python.org/3/c-api/module.html#initializing-c-modules
    module = PyModule_Create(&native_def);
    if (!module) {
        return NULL;
    }

    // Finalize the native class's definition. This handles initialization and
    // inheritance.
    //
    // See also: https://docs.python.org/3/c-api/type.html#c.PyType_Ready
    if (PyType_Ready(&native_model_type) < 0) {
        Py_DECREF(module);
        return NULL;
    }

    // Add the native class, a binding for model_t.
    Py_INCREF(&native_model_type);
    if (PyModule_AddObject(module, "model", (PyObject *)&native_model_type)) {
        Py_DECREF(module);
        return NULL;
    }

    return module;
}
