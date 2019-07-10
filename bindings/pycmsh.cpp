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
    "void config_timeout(double max_time)\n"
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
    "void config_conflicts(int64_t max_conflicts)\n"
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
    "int var()\n"
);

static PyObject *var(native_model *self, PyObject *) {
    check_null

    int new_variable = self->model->var();
    return PyLong_FromLong(new_variable);
}

PyDoc_STRVAR(cnf_doc,
    "int cnf(int var)\n"
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
    "int v_and(int left, int right)\n"
);

static PyObject *v_and(native_model *self, PyObject *args, PyObject *kwds) {
    v_op(v_and)
}

PyDoc_STRVAR(v_nand_doc,
    "int v_nand(int left, int right)\n"
);

static PyObject *v_nand(native_model *self, PyObject *args, PyObject *kwds) {
    v_op(v_nand)
}

PyDoc_STRVAR(v_or_doc,
    "int v_or(int left, int right)\n"
);

static PyObject *v_or(native_model *self, PyObject *args, PyObject *kwds) {
    v_op(v_or)
}

PyDoc_STRVAR(v_nor_doc,
    "int v_nor(int left, int right)\n"
);

static PyObject *v_nor(native_model *self, PyObject *args, PyObject *kwds) {
    v_op(v_nor)
}

PyDoc_STRVAR(v_xor_doc,
    "int v_xor(int left, int right)\n"
);

static PyObject *v_xor(native_model *self, PyObject *args, PyObject *kwds) {
    v_op(v_xor)
}

PyDoc_STRVAR(v_assert_doc,
    "void v_assert(int var)\n"
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
    "void v_assume(int var)\n"
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
    "void v_unassume(int var)\n"
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
    "lbool solve()\n"
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
    "bool val(int var)\n"
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
    if (ptr != NULL) {
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
