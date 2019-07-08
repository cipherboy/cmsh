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

typedef struct {
    PyObject_HEAD

    /* Members for cmsh's native bindings */
    model_t *model;
} native_model;

PyDoc_STRVAR(config_timeout_doc,
    "config_timeout(double max_time)\n"
);

#define check_null \
    if (self == NULL || self->model == NULL) { \
        PyErr_SetString(PyExc_ValueError, "Error! You need to initialize the native model before calling this function."); \
    }

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
    "config_conflicts(int64_t max_conflicts)\n"
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
    "var()\n"
);

static PyObject *var(native_model *self, PyObject *args) {
    check_null

    int new_variable = self->model->var();
    return PyLong_FromLong(new_variable);
}

static int model_init(native_model *self, PyObject *args, PyObject *kwds) {
    char *kwlist[] = {(char *)"threads", (char *)"gauss", NULL};
    int threads = 1;
    bool gauss = true;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "ip", kwlist, &threads, &gauss)) {
        return -1;
    }

    check_null

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
    {NULL, NULL, 0, NULL},
};

static PyTypeObject native_model_type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "cmsh._native.model",   // tp_name
    sizeof(native_model),   // tp_basicsize
    0, // tp_itemsize -- zero, since we don't increase in size based on the
       // number of elements we hold
    (destructor) model_dealloc, // tp_dealloc
    NULL, // tp_print
    NULL, // tp_getattr
    NULL, // tp_setattr
    NULL, // tp_as_async
    NULL, // tp_repr
    NULL, // tp_as_number
    NULL, // tp_as_sequence
    NULL, // tp_as_mapping
    NULL, // tp_hash
    NULL, // tp_call
    NULL, // tp_str
    NULL, // tp_getattro
    NULL, // tp_setattro
    NULL, // tp_as_buffer
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, // tp_flags
    NULL, // tp_doc
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
    0, // tp_free
    0, // tp_is_gc
    0, // tp_bases
    0, // tp_mro
    0, // tp_cache
    0, // tp_subclasses
    0, // tp_weaklist
    0, // tp_del
    0, // tp_version_tag
    0, // tp_finalize
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
