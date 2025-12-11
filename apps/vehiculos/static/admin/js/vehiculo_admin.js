(function() {
    'use strict';

    // Esperar a que Django jQuery esté disponible
    function waitForJQuery(callback) {
        if (typeof django !== 'undefined' && django.jQuery) {
            callback(django.jQuery);
        } else {
            setTimeout(function() { waitForJQuery(callback); }, 100);
        }
    }

    waitForJQuery(function($) {
        $(document).ready(function() {
            // Esperar a que Select2 se inicialice completamente
            setTimeout(initMarcaModeloFilter, 500);
        });

        function initMarcaModeloFilter() {
            // Select2 autocomplete usa un campo oculto y un span
            var $marcaField = $('#id_marca');
            var $modeloField = $('#id_modelo');
            var $modeloContainer = $modeloField.closest('.related-widget-wrapper');

            if (!$marcaField.length || !$modeloField.length) {
                console.log('Vehiculo admin: campos marca/modelo no encontrados');
                return;
            }

            console.log('Vehiculo admin: inicializando filtro marca-modelo');

            // Guardar el valor actual del modelo (para edicion)
            var currentModeloId = $modeloField.val();
            var currentModeloText = '';

            // Obtener texto del modelo actual si existe
            if ($modeloField.next('.select2').length) {
                currentModeloText = $modeloField.next('.select2').find('.select2-selection__rendered').text();
            }

            // Funcion para cargar modelos via AJAX
            function loadModelos(marcaId, selectedModeloId, selectedModeloText) {
                console.log('Cargando modelos para marca:', marcaId);

                if (!marcaId) {
                    // Limpiar el campo modelo
                    $modeloField.val('').trigger('change');
                    if ($modeloField.hasClass('select2-hidden-accessible')) {
                        $modeloField.select2('destroy');
                    }
                    $modeloField.html('<option value="">---------</option>');
                    initModeloSelect2(marcaId);
                    return;
                }

                $.ajax({
                    url: '/admin/vehiculos/vehiculo/ajax/modelos/',
                    data: { marca_id: marcaId },
                    dataType: 'json',
                    success: function(data) {
                        console.log('Modelos recibidos:', data.modelos ? data.modelos.length : 0);

                        // Destruir Select2 existente
                        if ($modeloField.hasClass('select2-hidden-accessible')) {
                            $modeloField.select2('destroy');
                        }

                        // Construir opciones
                        var options = '<option value="">---------</option>';
                        if (data.modelos && data.modelos.length > 0) {
                            data.modelos.forEach(function(modelo) {
                                var selected = (modelo.id == selectedModeloId) ? ' selected' : '';
                                options += '<option value="' + modelo.id + '"' + selected + '>' + modelo.nombre + '</option>';
                            });
                        }
                        $modeloField.html(options);

                        // Re-inicializar Select2 con búsqueda local
                        initModeloSelect2(marcaId);
                    },
                    error: function(xhr, status, error) {
                        console.error('Error cargando modelos:', error);
                    }
                });
            }

            function initModeloSelect2(marcaId) {
                if (!marcaId) {
                    // Sin marca, Select2 básico
                    $modeloField.select2({
                        width: '100%',
                        placeholder: 'Primero seleccione una marca'
                    });
                } else {
                    // Con marca, Select2 con búsqueda
                    $modeloField.select2({
                        width: '100%',
                        placeholder: 'Buscar modelo...',
                        allowClear: true
                    });
                }
            }

            // Escuchar cambios en marca
            // Para autocomplete_fields, el evento es diferente
            $marcaField.on('change', function(e) {
                var marcaId = $(this).val();
                console.log('Marca cambiada a:', marcaId);
                // No mantener el modelo anterior si cambia la marca
                loadModelos(marcaId, null, null);
            });

            // También escuchar eventos de Select2
            $marcaField.on('select2:select select2:clear', function(e) {
                var marcaId = $(this).val();
                console.log('Marca select2 evento:', marcaId);
                loadModelos(marcaId, null, null);
            });

            // Cargar modelos iniciales si hay una marca seleccionada (modo edicion)
            var initialMarcaId = $marcaField.val();
            console.log('Marca inicial:', initialMarcaId, 'Modelo inicial:', currentModeloId);

            if (initialMarcaId) {
                loadModelos(initialMarcaId, currentModeloId, currentModeloText);
            } else {
                // Inicializar modelo vacío
                if ($modeloField.hasClass('select2-hidden-accessible')) {
                    $modeloField.select2('destroy');
                }
                $modeloField.html('<option value="">---------</option>');
                initModeloSelect2(null);
            }
        }
    });
})();
